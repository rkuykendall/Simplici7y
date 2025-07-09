# Essential File Upload Optimizations for 30-Second Heroku Timeout

## The Real Problem

- Heroku kills any process after 30 seconds (hard limit, cannot be changed)
- Your uploads are currently at 800 KBps instead of your 428 Mbps connection
- Need to maximize upload speed to fit within 30 seconds

## Key Optimizations That Actually Help

### 1. S3 Multipart Uploads (MOST IMPORTANT)

```python
AWS_S3_MULTIPART_THRESHOLD = 1024 * 1024 * 5   # 5MB
AWS_S3_MULTIPART_CHUNKSIZE = 1024 * 1024 * 5   # 5MB
AWS_S3_MAX_CONCURRENCY = 10
AWS_S3_USE_THREADS = True
```

**Why this matters**: Uploads files in parallel 5MB chunks instead of one large stream

### 2. Memory Management

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
```

**Why this matters**: Prevents Django from loading huge files into memory, causing slowdowns

### 3. Realistic File Size Limits

At 800 KBps: 800 KB/s × 30s = 24 MB max
At full speed: 428 Mbps = 53.5 MB/s × 30s = 1.6 GB max

## What Was Removed (Not Helpful for 30s Limit)

- Custom upload handlers (Django's are fine)
- Progress tracking (nice-to-have, doesn't speed up uploads)
- Timeout extensions (impossible on Heroku)
- Complex middleware (adds overhead)

## Testing Strategy

1. Test with 10MB file (should work at current speed)
2. Test with 20MB file (pushing current limit)
3. Test with 50MB file (should work if optimizations help)

## Expected Results

If S3 multipart uploads work properly, you should see:

- Multiple parallel upload streams in network tab
- Much faster upload speeds
- Ability to upload larger files within 30 seconds

## The Bottom Line

The S3 multipart configuration is likely the most important change. Everything else is secondary.
