from useragents import search_strings

class Middleware(object):
    @staticmethod
    def process_request(request):
        """Adds a "mobile" attribute to the request which is True or False
           depending on whether the request should be considered to come from a
           small-screen device such as a phone or a PDA"""

        if request.has_key("HTTP_X_OPERAMINI_FEATURES"):
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            request.mobile = True
            return True

        if request.has_key("X-Operamini-Features"):
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            request.mobile = True
            return True

        if request.has_key("Content-Type"):
            s = request["Content-Type"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                # Then it's a wap browser
                request.mobile = True
                return True

        if request.has_key("Accept"):
            s = request["Accept"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                # Then it's a wap browser
                request.mobile = True
                return True

        if request.has_key("User-Agent"):
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            s = request["User-Agent"].lower()
            for ua in search_strings:
                if ua in s:
                    request.mobile = True
                    return True

        if request.has_key("Agent"):
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            s = request["User-Agent"].lower()
            for ua in search_strings:
                if ua in s:
                    request.mobile = True
                    return True

        #Otherwise it's not a mobile
        request.mobile = False
        return None

def detect_mobile(view):
    """View Decorator that adds a "mobile" attribute to the request which is
       True or False depending on whether the request should be considered
       to come from a small-screen device such as a phone or a PDA"""

    def detected(request, *args, **kwargs):
        Middleware.process_request(request)
        return view(request, *args, **kwargs)
    detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
    return detected


__all__ = ['Middleware', 'detect_mobile']
