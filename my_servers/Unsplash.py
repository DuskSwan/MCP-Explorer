import os
import ctypes
from pathlib import Path

import requests
from PIL import Image
from io import BytesIO

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 加载 .env 文件
load_dotenv()  
Unsplash_KEY = os.getenv("UNSPLASH_API")

# 初始化 MCP 服务器
mcp = FastMCP("wallpaper-server")

def analyze_response(response):
    """分析响应内容"""
    if response.status_code != 200:
        return f"请求失败，状态码: {response.status_code}"
    
    content_type = response.headers.get('Content-Type', '').lower()
    
    response_info = f"响应状态码: {response.status_code}\n响应内容类型: {content_type}\n"
    
    if 'json' in content_type:
        try:
            json_data = response.json()  # 解析 JSON 数据
            response_info += "响应内容（JSON 格式）：\n" + str(json_data)
        except ValueError:
            response_info += "响应内容不是有效的 JSON 格式"
    
    elif 'html' in content_type:
        response_info += "响应内容（HTML 格式）：\n" + response.text[:200] + "..."
    
    elif 'image' in content_type:
        image = Image.open(BytesIO(response.content))
        image.show()
        response_info += "图片已显示"
    
    elif 'plain' in content_type:
        response_info += "响应内容（纯文本）：\n" + response.text[:200] + "..."
    
    else:
        response_info += "响应内容类型未知，原始内容：\n" + response.text[:200] + "..."
    
    return response_info

@mcp.tool()
def show_img(image_url: str) -> str:
    """
    展示图片

    参数:
        image_url: 图片的URL地址字符串。
    返回:
        显示图片结果的字符串描述。
    
    """
    response = requests.get(image_url)
    try:
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.show()
            return "image show success"
        else:
            return f"request fails, error code: {response.status_code}"
    except Exception as e:
        return f"meet error: {str(e)}"

@mcp.tool()
def get_random_wallpaper() -> str:
    """get random wallpaper url"""
    url = f"https://api.unsplash.com/photos/random?query=wallpaper&client_id={Unsplash_KEY}"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            data = response.json()
            return data['urls']['raw']
        else:
            return f"Error status code: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_filter_image_url(query: str = 'nature', color: str = 'blue', 
                  orientation: str = 'landscape', page: int = 1, 
                  per_page: int = 30, order_by: str = 'popular', get_index: int = 0) -> str:
    """
    get flitter image url from unsplash using filters
    
    parameters:
        query: str, default 'nature', the keyword to search for.
        color: str, default 'blue', the color filter. ('black_and_white', 'black', 'white', 'yellow', 'orange', 'red', 'purple', 'magenta', 'green', 'teal', 'blue')
        orientation: str, default 'landscape', the orientation of the image.('landscape', 'portrait', 'squarish')
        page: int, default 1, the page number for pagination.
        per_page: int, default 30, number of results per page.
        order_by: str, default 'popular', the method to order.('latest', 'relevant', 'popular')
        get_index: int, default 0, the index of the image to return from the results.
    
    return:
        str: the url of the image or an error message.
    """
    url = f"https://api.unsplash.com/search/photos?client_id={Unsplash_KEY}"

    # 根据条件拼接URL
    if query:
        url += f"&query={query}"
    if color:
        url += f"&color={color}"
    if orientation:
        url += f"&orientation={orientation}"
    url += f"&page={page}&per_page={per_page}&order_by={order_by}"
    print(url)

    # 发送请求
    response = requests.get(url)
    
    # 处理响应
    try:
        if response.status_code == 200:
            data = response.json()
            if data:
                # 返回第get_index个图片的原始URL
                return data['results'][get_index]['urls']['raw']
            else:
                return "没有找到符合条件的图片。"
        else:
            return f"请求失败，状态码: {response.status_code}"
    except Exception as e:
        return f"遇到错误: {str(e)}"

@mcp.tool()
def download_one_image(image_url: str, save_dir: str = './imgs', img_name: str = "wallpaper.jpg") -> str:
    """
    download one image from the given URL and save it to the specified directory.

    parameters:
        image_url: str, the URL of the image to download.
        save_dir: str, default './imgs', the directory to save the image.
        img_name: str, default 'wallpaper.jpg', the name of the saved image file.
    
    return:
        str: success or failure message.
    """
    response = requests.get(image_url)
    if response.status_code == 200:
        save_path = Path(save_dir) / (img_name if img_name else "wallpaper.jpg")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return f"The image has been saved at {save_path.resolve()}"
    else:
        return f"Download failed, error code: {response.status_code}"

@mcp.tool()
def set_wallpaper(image_path: str) -> str:
    """
    set the wallpaper of the desktop to the image at the given path.

    parameters:
        image_path: str, the path to the image file.
    return:
        str: success or failure message.
    
    """
    unicode_image_path = ctypes.c_wchar_p(image_path)
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, unicode_image_path, 3)
    if result:
        return f"The wallpaper has been set to {image_path}"
    else:
        return "Setting wallpaper failed."

def test():
    url = get_filter_image_url(query='nature', color='blue', orientation='landscape')
    print(url)
    show_img(url)

if __name__ == "__main__":
    mcp.run(transport='stdio')
    # test()