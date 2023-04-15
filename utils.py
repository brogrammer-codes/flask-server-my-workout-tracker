def get_token(request):
    if(request):
        headers = request.headers
        bearer = headers.get('Authorization')    # Bearer YourTokenHere
        token = bearer.split()[1]
        return token
    return ''