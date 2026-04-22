locals {
  cdn_domain = var.route53_zone_id == "" ? null : "${var.cdn_subdomain}.${var.domain_name}"
}

resource "aws_cloudfront_origin_access_control" "images" {
  name                              = "${local.name_prefix}-images-oac"
  description                       = "OAC para bucket de imagenes"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_acm_certificate" "cdn" {
  count             = var.route53_zone_id == "" ? 0 : 1
  provider          = aws.us_east_1
  domain_name       = local.cdn_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cdn_cert_validation" {
  for_each = var.route53_zone_id == "" ? {} : {
    for dvo in aws_acm_certificate.cdn[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  zone_id = var.route53_zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "cdn" {
  count                   = var.route53_zone_id == "" ? 0 : 1
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.cdn[0].arn
  validation_record_fqdns = [for r in aws_route53_record.cdn_cert_validation : r.fqdn]
}

resource "aws_cloudfront_distribution" "images" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.name_prefix} imagenes"
  price_class         = "PriceClass_100"
  default_root_object = ""

  aliases = var.route53_zone_id == "" ? [] : [local.cdn_domain]

  origin {
    domain_name              = aws_s3_bucket.images.bucket_regional_domain_name
    origin_id                = "s3-images"
    origin_access_control_id = aws_cloudfront_origin_access_control.images.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-images"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.route53_zone_id == "" ? true : false
    acm_certificate_arn            = var.route53_zone_id == "" ? null : aws_acm_certificate_validation.cdn[0].certificate_arn
    ssl_support_method             = var.route53_zone_id == "" ? null : "sni-only"
    minimum_protocol_version       = var.route53_zone_id == "" ? "TLSv1" : "TLSv1.2_2021"
  }
}

# Sólo CloudFront puede leer el bucket.
data "aws_iam_policy_document" "s3_images_policy" {
  statement {
    sid     = "AllowCloudFrontRead"
    actions = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.images.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.images.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "images" {
  bucket = aws_s3_bucket.images.id
  policy = data.aws_iam_policy_document.s3_images_policy.json
}

resource "aws_route53_record" "cdn_alias" {
  count   = var.route53_zone_id == "" ? 0 : 1
  zone_id = var.route53_zone_id
  name    = local.cdn_domain
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.images.domain_name
    zone_id                = aws_cloudfront_distribution.images.hosted_zone_id
    evaluate_target_health = false
  }
}
