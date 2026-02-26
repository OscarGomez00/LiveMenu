import asyncio
import os
import uuid
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Función pura para procesamiento CPU-bound (debe estar fuera de la clase para ser pickleable)
def process_image_sync(input_bytes: bytes, output_path: str, size: tuple[int, int], quality: int):
    """
    Procesamiento síncrono de imagen (CPU-bound).
    Pensado para ser ejecutado en un ProcessPoolExecutor.
    """
    from io import BytesIO
    from PIL import Image
    
    img = Image.open(BytesIO(input_bytes))
    
    # Convertir a RGB si es necesario
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Redimensionar
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Guardar en WebP
    img.save(output_path, "WEBP", quality=quality)
    return True

class ImageWorkerPool:
    """
    Orquestador de procesamiento de imágenes con asyncio.Queue y ProcessPoolExecutor.
    Gestiona la concurrencia y el ciclo de vida del procesamiento.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageWorkerPool, cls).__new__(cls)
            cls._instance.queue = None
            cls._instance.executor = None
            cls._instance.is_running = False
            cls._instance.workers = []
        return cls._instance

    async def start(self):
        """Inicia los workers consumidores."""
        if self.is_running:
            return
        
        # Iniciar recursos solo cuando se necesiten (dentro de un loop activo)
        if self.queue is None:
            self.queue = asyncio.Queue(maxsize=settings.IMAGE_QUEUE_SIZE)
            
        if self.executor is None:
            self.executor = ProcessPoolExecutor(max_workers=settings.IMAGE_WORKERS)
            
        self.is_running = True
        self.workers = [] # Limpiar posibles referencias antiguas
        for i in range(settings.IMAGE_WORKERS):
            worker = asyncio.create_task(self._worker_loop(i))
            self.workers.append(worker)
        print(f"DEBUG: Worker Pool iniciado con {settings.IMAGE_WORKERS} workers.")

    async def stop(self):
        """Apagado ordenado del pool."""
        if not self.is_running:
            return
            
        print("DEBUG: Iniciando apagado ordenado del ImageWorkerPool...")
        
        # 1. Esperar a que la cola se vacíe (máximo 10s)
        try:
            if self.queue and self.queue.qsize() > 0:
                print(f"DEBUG: Esperando a que terminen {self.queue.qsize()} tareas pendientes...")
                await asyncio.wait_for(self.queue.join(), timeout=10.0)
        except asyncio.TimeoutError:
            print("WARNING: Tiempo de espera agotado para vaciar la cola.")
        except Exception as e:
            print(f"Error esperando cola: {e}")

        self.is_running = False
        
        # 2. Cancelar y limpiar workers de asyncio
        for worker in self.workers:
            worker.cancel()
        
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
        
        # 3. Limpiar cola
        self.queue = None
        
        # 4. Cerrar el executor de procesos
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
            
        print("DEBUG: Worker Pool apagado correctamente.")

    async def _worker_loop(self, worker_id: int):
        """Ciclo principal de cada worker consumidor."""
        while self.is_running:
            try:
                # Obtener tarea de la cola
                task = await self.queue.get()
                input_bytes, output_path, future = task
                
                # Ejecutar procesamiento CPU-bound en el executor de procesos
                loop = asyncio.get_running_loop()
                try:
                    await loop.run_in_executor(
                        self.executor,
                        process_image_sync,
                        input_bytes,
                        output_path,
                        settings.DISH_IMAGE_SIZE,
                        settings.IMAGE_QUALITY
                    )
                    future.set_result(True)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en worker {worker_id}: {e}")

    async def enqueue_dish_image(self, file_content: bytes) -> str:
        """
        Encola una imagen para procesar y espera su resultado (asíncrono-esperado).
        """
        if not self.is_running:
            raise HTTPException(status_code=503, detail="Servicio de procesamiento no disponible")
            
        filename = f"{uuid.uuid4()}.webp"
        # Asegurar directorio
        output_dir = Path(settings.UPLOAD_DIR) / "dishes"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / filename)
        
        # Future para capturar el resultado del worker
        future = asyncio.get_running_loop().create_future()
        
        # Encolar tareas con timeout si la cola está llena
        try:
            await asyncio.wait_for(
                self.queue.put((file_content, output_path, future)),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=503, detail="Cola de procesamiento llena")
        
        # Esperar a que el worker termine con un timeout razonable (ej: 30s)
        try:
            await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Tiempo de procesamiento excedido")
        
        return f"/uploads/dishes/{filename}"

# Instancia global para ser usada en los endpoints
image_pool = ImageWorkerPool()
