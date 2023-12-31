from django.templatetags.static import static
from main.models import Interest

def global_data(request):
    return {
        'fallback_images' : [
        static('resource/1.jpg'),
        static('resource/2.jpg'),
        static('resource/3.jpg'),
        static('resource/4.jpg'),
        static('resource/5.jpg'),
        static('resource/6.jpg'),
        static('resource/7.jpg'),
        static('resource/8.jpg')
    ],
        'empty_user': static('resource/empty_user.png'),
        'categories' : Interest.objects.all(),
        
    }