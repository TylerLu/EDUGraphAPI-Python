from django.utils.deprecation import MiddlewareMixin
 
class ExternalInfoMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.ms_user = ''
        request.ms_token = None
        request.aad_token = None
