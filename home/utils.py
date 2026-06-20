from django.core.cache import cache
from django.utils.timezone import now, timedelta
from .models import BlockedIP


class BruteForceLoginProctection:
    def __init__(self, request=None):
        self.request = request
        self.default_attemp = 1
        self.default_timeout = 300  # in seconds
        self.default_level_of_times = 1
        self.default_max_attempts = 5
        self.default_block_until = None
        self.max_level_of_times = 8
        self.level = {
            # level_key : (max_attempts, block_duration_in_seconds, string_for_message)
            1: (self.default_max_attempts, self.default_timeout, '5 minutes'),
            2: (self.default_max_attempts - 2, 3600, '1 hour'),
            3: (self.default_max_attempts - 2, 86400, '24 hours'),
            4: (self.default_max_attempts - 2, 604800, '7 days'),
            5: (self.default_max_attempts - 2, 2592000, '30 days'),
            6: (self.default_max_attempts - 2, 7776000, '90 days'),
            7: (self.default_max_attempts - 2, 15552000, '180 days'),
            8: (self.default_max_attempts - 2, 31536000, '365 days'),
        }
        self.get_client_ip()


    def handle(self):
        message = ''
        
        # if request.path.startswith("/login/"): 
        #    if you want to apply this protection specific page page then uncomment above line and indent the below code with one more level
        current_time = now()
        cached_value = cache.get(f"b_{self.ip}", None)
        
        if cached_value:
            level_of_times, attempts, block_until, last_attempt_time = cached_value
            
            # if user reached the max_attempts
            if attempts >= self.level[level_of_times][0]:
                # if user try to login again after blocked time over(due to to many try in given time) and failed again then  increase the level_of_times(moving toward second time blocked and more time)
                if block_until and now() >= block_until:
                    if self.max_level_of_times >= (level_of_times + 1):
                        cache.set(f"b_{self.ip}", (level_of_times + 1, self.default_attemp, self.default_block_until, current_time), timeout=self.level[level_of_times+1][1])
                        message = f"Wrong details. You have {self.level[level_of_times+1][0] - self.default_attemp} more attempts left before being blocked for {self.level[level_of_times+1][2]}."
                    else:
                        self.blocked_ip()
                        message = "Too many attempts. You are permanently blocked. Please contact support."
                
                # if user attempting even during block time then do not increase the level just return simple message that ure blocked until specific time
                elif block_until and now() < block_until:
                    message = f"Too many attempts. You are blocked for {self.level[level_of_times][2]}. Please try again later."
                
                # block user ip after it reached its max_attempt for specific time
                else:
                    block_until = current_time + timedelta(seconds=self.level[level_of_times][1])
                    cache.set(f"b_{self.ip}", (level_of_times, attempts + 1, block_until, current_time), timeout=self.level[level_of_times][1])
                    message = f"Too many attempts. You are blocked for {self.level[level_of_times][2]}. Please try again later."
            else:
                #increase the attempts till it reaches the max allowed but do not block the user until max attempts reached
                cache.set(f"b_{self.ip}", (level_of_times, attempts + 1, self.default_block_until, current_time), timeout=self.level[level_of_times][1])
                message = f"Wrong details. You have {self.level[level_of_times][0] - attempts} more attempts left before being blocked for {self.level[level_of_times][2]}."

        else:
            # start tracking form first wrong attempt
            cache.set(f"b_{self.ip}", (self.default_level_of_times, self.default_attemp, self.default_block_until, current_time), timeout=self.default_timeout)
            message = f"Wrong details. You have {self.default_max_attempts - self.default_attemp} more attempts left before being blocked for 5 minutes."

        return message
    
    def get_client_ip(self):
        if self.request:
            x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                self.ip = x_forwarded_for.split(",")[0].strip()  # Can contain multiple IPs: client, proxy1, proxy2
            else:
                self.ip = self.request.META.get("REMOTE_ADDR")
        else:
            raise ValueError("Request object is required to get client IP.")
    
    def blocked_ip(self, ip=None):
        if self.ip or ip:
            BlockedIP.objects.get_or_create(ip_address=self.ip)
        else:
            raise NameError("ip attribute is required to block IP. please call get_client_ip method first to set self.ip")
    
    def check_blocked_ip(self, ip=None):
        if self.ip or ip:
            return BlockedIP.objects.filter(ip_address=self.ip).exists()
        else:
            raise NameError("ip attribute is required to check blocked IP. please call get_client_ip method first to set self.ip")