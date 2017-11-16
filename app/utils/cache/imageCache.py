import random
import string
# pip install Pillow
# Image:是一个画板(context),ImageDraw:是一个画笔, ImageFont:画L import Image, ImageDraw, ImageFont
from PIL import Image, ImageDraw, ImageFont
from . import captcha


class ImageCaptcha:  # Captcha验证码
    # 把一些常量抽取成类属性
    # 字体的位置
    font_path = 'utils/cache/verdana.ttf'
    # font_path = '/root/bbs/app/utils/cache/verdana.ttf'
    # 在liunx云主机中使用

    # 生成几位数的验证码
    number = 4
    # 生成验证码图片的宽度和高度
    size = (100, 45)
    # 背景颜色，默认为白色 RGB(Re,Green,Blue)
    bg_color = (255, 255, 255)
    # 随机字体颜色
    font_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
    # 验证码字体大小
    font_size = 28
    # 随机干扰线颜色。
    line_color = (random.randint(0, 220), random.randint(0, 255), random.randint(0, 100))
    # 是否要加入干扰线
    draw_line = True
    # 是否绘制干扰点
    draw_point = True
    # 加入干扰线的条数
    line_number = 1

    SOURCE = set(string.ascii_letters + string.digits) - {'i', 'l', 'L', 'I', '1', 'o', 'O', '0'}
    # 用来随机生成一个字符串(包括英文和数字),排除这几个容易混淆的
    # 定义成类方法,然后是私有的,对象在外面不能直接调用

    @classmethod
    def gene_text(cls):
        return ''.join(random.sample(cls.SOURCE, cls.number))  # number是生成验证码的位数

    # 用来绘制干扰线
    @classmethod
    def __gene_line(cls, draw, width, height):
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([begin, end], fill=cls.line_color)

    # 用来绘制干扰点
    @classmethod
    def __gene_points(cls, draw, point_chance, width, height):
        chance = min(100, max(0, int(point_chance))) # 大小限制在[0, 100]
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    #生成验证码
    @classmethod
    def gene_code(cls):
        width, height = cls.size  # 宽和高
        image = Image.new('RGBA', (width,height), cls.bg_color)  # 创建图片
        font = ImageFont.truetype(cls.font_path, cls.font_size)  # 验证码的字体
        draw = ImageDraw.Draw(image)  # 创建画笔
        text = cls.gene_text()  # 生成字符串
        font_width, font_height = font.getsize(text)
        draw.text(((width - font_width) / 2, (height - font_height) / 2), text, font= font, fill=cls.font_color) #填充字符串
        # 如果需要绘制干扰线
        if cls.draw_line:
            # 遍历line_number次,就是画line_number根线条
            for x in range(0, cls.line_number):
                cls.__gene_line(draw,width,height)
        # 如果需要绘制噪点
        if cls.draw_point:
            cls.__gene_points(draw,10,width,height)
        return (text, image)

    @classmethod
    def check_captcha(cls, cache):
        captcha_lower = cache.lower()
        if captcha.get(captcha_lower):
            captcha.delete(captcha_lower)
            return True
        else:
            return False
