import requests
import json
import os

# API 接口
course_list_url = "https://earthworm.cuixueshe.com/api/course-pack/p3yk3vz0hlrjmllcioibchww"
course_detail_url_template = "https://earthworm.cuixueshe.com/api/course-pack/p3yk3vz0hlrjmllcioibchww/courses/{}"
llama_api_url = "http://localhost:11434/api/generate"


def get_course_list():
    # 获取课程列表
    response = requests.get(course_list_url)
    response.raise_for_status()
    return response.json()


def get_course_detail(course_id, course_number):
    # 获取指定课程的详细信息并打印日志
    url = course_detail_url_template.format(course_id)
    response = requests.get(url)
    response.raise_for_status()
    print(f"课程 {course_number} 已加载")
    return response.json()


def generate_article(descriptions):
    # 设置明确的 prompt
    prompt = '''
**Act like an expert English language tutor who specializes in helping Chinese-speaking students improve their English reading comprehension skills. You have been teaching English for over 15 years and are proficient in both English and Chinese.**

## Objective
I am learning English and have studied the following basic phrases and sentences: {}. Please generate a reading comprehension article of approximately 100 to 200 words to help me practice and improve my English. The article should primarily include the phrases and sentences I have learned. You may include a few new words or phrases to challenge me, but avoid overly complex vocabulary.

## Instructions
1. **Vocabulary List**: Provide a list of words used in the article, including their Chinese translations and pronunciations.
   - Format the vocabulary list as follows:
     | 单词 | 发音 | 解释 |
     |------|------|------|
     | Word | /pronunciation/ | Chinese translations |

2. **English Article**: Write a 100 to 200-word article using the provided phrases and sentences. Ensure the article is coherent and meaningful.

3. **Chinese Translations**: Follow the article with a clear and fluent Chinese translations of the content to help me better understand and learn from the reading material.

### Vocabulary List
| 单词 | 发音 | 解释 |
|------|------|------|
| Word | /pronunciation/ | Chinese translations |

### English Article
[Insert article here]

### 中文翻译
[Insert Chinese translations here]

Take a deep breath and work on this problem step-by-step.
    '''
    prompt = prompt.format(descriptions)

    print("=================")
    print(prompt)
    print("=================")

    # 发送请求到 LLaMA API
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
    }
    response = requests.post(llama_api_url, json=payload, stream=True)
    response.raise_for_status()

    # 初始化空的生成内容
    generated_text = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            try:
                json_line = json.loads(decoded_line)
                generated_text += json_line.get("response", "")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    return generated_text


def save_to_md(directory, filename, content):
    # 确保目录存在
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 将内容保存到 Markdown 文件中
    filepath = os.path.join(directory, filename)
    with open(filepath, "w") as file:
        file.write(content)
    print(f"内容已保存到 {filepath}")


def main():
    # 获取课程列表
    course_list = get_course_list()
    courses = course_list.get("courses", [])

    if not courses:
        print("未找到任何课程。")
        return

    # 打印课程列表
    for index, course in enumerate(courses, start=1):
        course_title = course.get("title")
        print(f"课程编号: {index}, 标题: {course_title}")

    # 用户选择生成内容的选项
    print("请选择一个选项:")
    print("1. Generate content for a specific lesson. \n   生成单独某一课的内容。")
    print("2. Generate content for a specific lesson and all previous lessons. \n   生成某一课及其以前的内容。")
    print("3. Generate content for all lessons and save each to a separate file. \n   生成每一课的内容并保存到对应的文件。")
    choice = input("请输入您的选择 (1/2/3): ")

    base_dir = "generated_articles"

    if choice == '1':
        # 生成单独某一课的内容
        lesson_number = int(input("请输入课程的编号: "))
        selected_course = courses[lesson_number - 1]
        selected_course_id = selected_course.get("id")
        course_detail = get_course_detail(selected_course_id, lesson_number)
        statements = course_detail.get("statements", [])
        descriptions = ""
        english_set = set()
        for stmt in statements:
            english_phrase = stmt['english']
            if english_phrase not in english_set:
                english_set.add(english_phrase)
                descriptions += f"({english_phrase})、"
        article = generate_article(descriptions)
        print(f"\n根据课程 {lesson_number} 生成的文章:\n")
        print(article)
        save_to_md(os.path.join(base_dir, "specific_lesson"), f"lesson_{lesson_number}.md", article)

    elif choice == '2':
        # 生成某一课及其以前的内容
        lesson_number = int(input("请输入已学到的课程编号: "))
        new_lesson_number = 1
        selected_courses = courses[:lesson_number]
        combined_description = ""
        english_set = set()
        print(selected_courses)
        for course in selected_courses:
            course_id = course.get("id")
            course_detail = get_course_detail(course_id, new_lesson_number)
            statements = course_detail.get("statements", [])
            for stmt in statements:
                english_phrase = stmt['english']
                if english_phrase not in english_set:
                    english_set.add(english_phrase)
                    combined_description += f"({english_phrase})、"
            new_lesson_number = new_lesson_number + 1
        article = generate_article(combined_description)
        print(f"\n根据课程 {lesson_number} 及其以前的内容生成的文章:\n")
        print(article)
        save_to_md(os.path.join(base_dir, "up_to_lesson"), f"up_to_lesson_{lesson_number}.md", article)

    elif choice == '3':
        # 生成每一课的内容并保存到对应的文件
        for index, course in enumerate(courses, start=1):
            course_id = course.get("id")
            course_title = course.get("title")
            course_detail = get_course_detail(course_id, index)
            statements = course_detail.get("statements", [])
            descriptions = ""
            english_set = set()
            for stmt in statements:
                english_phrase = stmt['english']
                if english_phrase not in english_set:
                    english_set.add(english_phrase)
                    descriptions += f"({english_phrase})、"
            article = generate_article(descriptions)
            save_to_md(os.path.join(base_dir, "all_lessons"), f"lesson_{index}.md", article)
    else:
        print("无效的选择。请重新启动程序并选择一个有效的选项。")


if __name__ == "__main__":
    main()
