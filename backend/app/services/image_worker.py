import asyncio
import uuid
from concurrent.futures import ProcessPoolExecutor
from fastapi import HTTPException
from app.core.config import settings
from app.services.storage import get_storage


# CPU-bound: debe estar fuera de la clase para ser pickleable por ProcessPoolExecutor.
# Devuelve {variant: (key, bytes)}; la subida la hace el loop asíncrono.
def process_image_sync(input_bytes: bytes, base_name: str, sizes: dict, quality: int):
    from io import BytesIO
    from PIL import Image

    img = Image.open(BytesIO(input_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    results = {}
    for variant_name, size in sizes.items():
        variant_img = img.copy()
        variant_img.thumbnail(size, Image.Resampling.LANCZOS)
        buf = BytesIO()
        variant_img.save(buf, "WEBP", quality=quality)
        key = f"dishes/{base_name}_{variant_name}.webp"
        results[variant_name] = (key, buf.getvalue())

    return results

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
                input_bytes, base_name, future = task

                loop = asyncio.get_running_loop()
                try:
                    variants = await loop.run_in_executor(
                        self.executor,
                        process_image_sync,
                        input_bytes,
                        base_name,
                        settings.IMAGE_SIZES,
                        settings.IMAGE_QUALITY,
                    )

                    storage = get_storage()
                    urls = {}
                    for variant_name, (key, data) in variants.items():
                        urls[variant_name] = await loop.run_in_executor(
                            None, storage.put_bytes, key, data, "image/webp"
                        )
                    future.set_result(urls)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en worker {worker_id}: {e}")

    async def enqueue_dish_image(self, file_content: bytes) -> dict:
        """
        Encola una imagen para procesar y espera su resultado.
        Retorna dict con URLs de las 3 variantes: thumbnail, medium, large.
        """
        if not self.is_running:
            raise HTTPException(status_code=503, detail="Servicio de procesamiento no disponible")
            
        base_name = str(uuid.uuid4())

        # Future para capturar el resultado del worker
        future = asyncio.get_running_loop().create_future()

        # Encolar tareas con timeout si la cola está llena
        try:
            await asyncio.wait_for(
                self.queue.put((file_content, base_name, future)),
                timeout=5.0,
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=503, detail="Cola de procesamiento llena")
        
        # Esperar a que el worker termine con un timeout razonable
        try:
            result = await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Tiempo de procesamiento excedido")
        
        return result

# Instancia global para ser usada en los endpoints
image_pool = ImageWorkerPool()
