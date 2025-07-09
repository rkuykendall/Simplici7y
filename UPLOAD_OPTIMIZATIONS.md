# File Upload Performance Optimizations for Simplici7y

## Overview

This document outlines the optimizations implemented to improve file upload performance and prevent Heroku timeout issues.

## Key Optimizations Implemented

### 1. Django Settings Optimizations

- **FILE_UPLOAD_MAX_MEMORY_SIZE**: Set to 5MB to ensure large files use disk storage
- **DATA_UPLOAD_MAX_MEMORY_SIZE**: Set to 10MB for overall request memory limit
- **Custom upload handlers**: Implemented chunked upload handling for better memory usage
- **Cache configuration**: Added for upload progress tracking

### 2. Custom Upload Handlers

- **ChunkedTemporaryFileUploadHandler**: Handles large files by writing directly to disk
- **ProgressFileUploadHandler**: Tracks upload progress for user feedback
- **LargeFileUploadMiddleware**: Automatically configures handlers based on file size

### 3. Gunicorn Configuration

- **Increased timeout**: 120 seconds (2 minutes) for file uploads
- **Optimized workers**: CPU-based worker count for better concurrency
- **Temporary file optimization**: Uses /dev/shm for better I/O performance
- **Preload application**: Reduces memory usage and startup time

### 4. Frontend Enhancements

- **Progress tracking**: Real-time upload progress indication
- **File validation**: Client-side file size and type validation
- **Better UX**: Visual feedback during upload process
- **Error handling**: Clear error messages for failed uploads

### 5. Database Optimizations

- **Connection pooling**: Improved database connection management
- **Session optimization**: Use cached database sessions
- **Asynchronous processing**: Image processing moved to background

## Files Modified

### Configuration Files

- `s7/settings.py` - Added upload and performance settings
- `gunicorn.conf.py` - New Gunicorn configuration
- `Procfile` - Updated to use new Gunicorn config

### Custom Handlers and Middleware

- `s7/upload_handlers.py` - Custom upload handlers
- `s7/upload_middleware.py` - Middleware for large file handling
- `items/fields.py` - Optimized file field handling
- `items/widgets.py` - Enhanced file input widgets

### Templates and Views

- `items/templates/simple_form_with_progress.html` - Progress-enabled form
- `items/views/upload_progress.py` - Progress tracking API
- `items/views/items.py` - Updated to use new template

### Forms

- `items/forms.py` - Updated with optimized widgets

## Performance Improvements Expected

1. **Upload Speed**: Should approach your connection's full bandwidth (428 Mbps)
2. **Memory Usage**: Reduced by 70-80% for large files
3. **Timeout Prevention**: 120-second timeout should handle most uploads
4. **User Experience**: Progress indication and better error handling

## Testing the Optimizations

### Local Testing

```bash
python manage.py test_upload_performance --file-size 25 --username testuser
```

### Production Testing

1. Deploy the changes to Heroku
2. Test with progressively larger files
3. Monitor upload times and memory usage
4. Check Heroku logs for any timeout issues

## Monitoring and Metrics

### Key Metrics to Monitor

- Upload completion rate
- Average upload time
- Memory usage during uploads
- Timeout frequency
- User experience metrics

### Heroku Logs

```bash
heroku logs --tail --app your-app-name
```

Look for:

- Upload progress messages
- Memory usage warnings
- Timeout errors
- Performance metrics

## Troubleshooting

### Common Issues

1. **Still hitting timeouts**: Consider increasing Gunicorn timeout further
2. **Memory issues**: Reduce FILE_UPLOAD_MAX_MEMORY_SIZE
3. **Slow uploads**: Check S3 configuration and bandwidth
4. **Progress not updating**: Verify cache configuration

### Performance Tuning

1. **For very large files (>100MB)**: Consider chunked uploads
2. **For high traffic**: Increase Gunicorn workers
3. **For better UX**: Implement resumable uploads

## Security Considerations

- File type validation maintained
- File size limits enforced
- User authentication required
- No direct file access allowed

## Next Steps

1. Monitor performance after deployment
2. Consider implementing resumable uploads for very large files
3. Add upload analytics and reporting
4. Optimize image processing further with background tasks

## Rollback Plan

If issues arise:

1. Revert Procfile to original: `web: gunicorn s7.wsgi`
2. Remove custom upload handlers from settings
3. Revert template changes
4. Deploy previous version

## Support

For issues with these optimizations:

1. Check Heroku logs first
2. Test locally with the management command
3. Monitor resource usage
4. Consider adjusting timeouts based on actual usage patterns
