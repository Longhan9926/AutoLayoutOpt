import random  # 调用random、string模块
import string


def random_name(count):
    src_digits = string.digits  # string_数字
    src_uppercase = string.ascii_uppercase  # string_大写字母
    src_lowercase = string.ascii_lowercase  # string_小写字母

    for i in range(count):
        # 随机生成数字、大写字母、小写字母的组成个数（可根据实际需要进行更改）
        digits_num = random.randint(1, 12)
        uppercase_num = random.randint(1, 36 - digits_num - 1)
        lowercase_num = 36 - (digits_num + uppercase_num)

        # 生成字符串
        password = random.choices(src_digits, k = digits_num) + random.choices(src_uppercase, k = uppercase_num) + \
                   random.choices(src_lowercase, k = lowercase_num)

        # 打乱字符串
        random.shuffle(password)

        # 列表转字符串
        new_password = ''.join(password)
        return new_password


if __name__ == '__main__':
    random_name(1)
