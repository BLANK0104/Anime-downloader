import re 
import requests as r
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

s = r.session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
})

def step_2(s, seperator, base=10):
    """
    Decode the encoded value using the specified base and separator.
    
    Args:
        s (str): The encoded string
        seperator (int): The separator value used in the encoding
        base (int): The base to use for decoding
        
    Returns:
        str: The decoded value
    """
    mapped_range = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
    numbers = mapped_range[0:base]
    max_iter = 0
    for index, value in enumerate(s[::-1]):
        max_iter += int(value if value.isdigit() else 0) * (seperator**index)
    mid = ''
    while max_iter > 0:
        mid = numbers[int(max_iter % base)] + mid
        max_iter = (max_iter - (max_iter % base)) / base
    return mid or '0'

def step_1(data, key, load, seperator):
    """
    Decode the obfuscated data to extract the form URL and token.
    
    Args:
        data (str): The obfuscated data string
        key (str): The key used for decoding
        load (int): The load value for character transformation
        seperator (int): The separator value used in decoding
        
    Returns:
        tuple: (form_url, token) extracted from the decoded data
    """
    payload = ""
    i = 0
    seperator = int(seperator)
    load = int(load)
    
    try:
        while i < len(data):
            s = ""
            while i < len(data) and data[i] != key[seperator]:
                s += data[i]
                i += 1
            if i < len(data):  # Only process if we didn't reach the end
                for index, value in enumerate(key):
                    s = s.replace(value, str(index))
                payload += chr(int(step_2(s, seperator, 10)) - load)
                i += 1
    except IndexError as e:
        logger.error(f"Index error during decoding: {e}")
        raise ValueError(f"Failed to decode data. Data length: {len(data)}, Current position: {i}")
    
    # Add error handling for the regex match
    matches = re.findall(r'action="([^\"]+)" method="POST"><input type="hidden" name="_token"\s+value="([^\"]+)', payload)
    
    if not matches:
        # Try alternative regex patterns
        alt_patterns = [
            r'<form action="([^"]+)".*?<input type="hidden" name="_token" value="([^"]+)"',
            r'action=[\'\"]([^\'\"]+)[\'\"].*?name=[\'\"_token[\'\"]\s+value=[\'\"]([^\'\"]+)[\'\"]',
            r'<form.*?action="([^"]+)".*?<input.*?name="_token".*?value="([^"]+)"'
        ]
        
        for pattern in alt_patterns:
            matches = re.findall(pattern, payload)
            if matches:
                logger.info(f"Found match with alternative pattern: {pattern}")
                break
        
        if not matches:
            logger.error("Failed to extract token from payload")
            sample = payload[:200] + "..." if len(payload) > 200 else payload
            raise ValueError(f"Could not find form action and token. Website structure may have changed. Payload sample: {sample}")
    
    return matches[0]

def get_dl_link(link: str):
    """
    Extract the direct download link from the kwik.cx page.
    
    Args:
        link (str): The kwik.cx URL
        
    Returns:
        str: The direct download URL
    """
    try:
        logger.info(f"Accessing link: {link}")
        resp = s.get(link)
        
        if resp.status_code != 200:
            raise ValueError(f"Failed to access kwik.cx page. Status code: {resp.status_code}")
        
        # Try to find the obfuscated data parameters
        params_match = re.findall(r'\("(\S+)",\d+,"(\S+)",(\d+),(\d+)', resp.text)
        
        if not params_match:
            # Try alternative patterns
            alt_patterns = [
                r'=\s*\("(\S+)",\d+,"(\S+)",(\d+),(\d+)',
                r'\(\'(\S+)\',\d+,\'(\S+)\',(\d+),(\d+)',
                r'=\s*\([\'\"](\S+)[\'\"],\d+,[\'\"](\S+)[\'\"],(\d+),(\d+)'
            ]
            
            for pattern in alt_patterns:
                params_match = re.findall(pattern, resp.text)
                if params_match:
                    logger.info(f"Found obfuscation params with alternative pattern")
                    break
        
        if not params_match:
            # As a last resort, try to find the direct source
            source_match = re.search(r'source\s+src="([^"]+)"', resp.text)
            if source_match:
                logger.info("Found direct source link")
                return source_match.group(1)
            
            # We can't extract the parameters
            sample = resp.text[:200] + "..." if len(resp.text) > 200 else resp.text
            raise ValueError(f"Could not find obfuscation parameters. Page structure has changed. Sample: {sample}")
        
        data, key, load, seperator = params_match[0]
        logger.info(f"Found obfuscation params: key length={len(key)}, data length={len(data)}")
        
        url, token = step_1(data=data, key=key, load=load, seperator=seperator)
        logger.info(f"Extracted URL: {url} and token")
        
        data = {"_token": token}
        headers = {'referer': link}
        
        resp = s.post(url=url, data=data, headers=headers, allow_redirects=False)
        
        if 'location' not in resp.headers:
            raise ValueError("No redirect location found in response headers")
        
        download_link = resp.headers["location"]
        logger.info(f"Extracted download link: {download_link}")
        
        return download_link
        
    except Exception as e:
        logger.error(f"Error in get_dl_link: {str(e)}")
        raise ValueError(f"Failed to extract download link: {str(e)}")

# Fallback method if the obfuscation method doesn't work
def get_dl_link_fallback(link: str):
    """
    Fallback method to extract download link using direct HTML parsing.
    
    Args:
        link (str): The kwik.cx URL
        
    Returns:
        str: The direct download URL
    """
    try:
        logger.info(f"Using fallback method for: {link}")
        resp = s.get(link)
        
        # Try to find direct video source
        source_match = re.search(r'source\s+src="([^"]+)"', resp.text)
        if source_match:
            return source_match.group(1)
        
        # Try to find the form and submit it manually
        form_match = re.search(r'<form action="([^"]+)".*?<input type="hidden" name="_token" value="([^"]+)"', resp.text, re.DOTALL)
        if form_match:
            url, token = form_match.groups()
            data = {"_token": token}
            headers = {'referer': link}
            
            resp = s.post(url=url, data=data, headers=headers, allow_redirects=False)
            if 'location' in resp.headers:
                return resp.headers["location"]
        
        raise ValueError("Could not extract download link with fallback method")
    except Exception as e:
        logger.error(f"Error in fallback method: {str(e)}")
        raise ValueError(f"Fallback method failed: {str(e)}")