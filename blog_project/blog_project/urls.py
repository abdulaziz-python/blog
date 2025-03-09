from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('blog.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', lambda request: redirect_to_api(request), name='home'),
]

def redirect_to_api(request):
    from django.http import HttpResponse
    return HttpResponse(
        """
        <html>
            <head>
                <title>Abdulaziz's Blog API</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    h1 {
                        color: #333;
                        border-bottom: 1px solid #eee;
                        padding-bottom: 10px;
                    }
                    a {
                        color: #0066cc;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                    .endpoint {
                        background: #f5f5f5;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 10px 0;
                    }
                </style>
            </head>
            <body>
                <h1>Welcome to Abdulaziz's Blog API</h1>
                <p>This is the API server for the blog. Below are the available endpoints:</p>
                
                <div class="endpoint">
                    <a href="/api/">/api/</a> - API Root with all available endpoints
                </div>
                
                <div class="endpoint">
                    <a href="/api/posts/">/api/posts/</a> - List all blog posts
                </div>
                
                <div class="endpoint">
                    <a href="/api/categories/">/api/categories/</a> - List all categories
                </div>
                
                <div class="endpoint">
                    <a href="/api/tags/">/api/tags/</a> - List all tags
                </div>
                
                <div class="endpoint">
                    <a href="/admin/">/admin/</a> - Admin interface
                </div>
                
                <p>For more information, please refer to the API documentation.</p>
            </body>
        </html>
        """,
        content_type="text/html"
    )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

