import requests
import json
import os
import concurrent.futures

# API 接口
COURSE_LIST_URL = "https://earthworm.cuixueshe.com/api/course-pack/p3yk3vz0hlrjmllcioibchww"
COURSE_DETAIL_URL_TEMPLATE = "https://earthworm.cuixueshe.com/api/course-pack/p3yk3vz0hlrjmllcioibchww/courses/{}"
LLAMA_API_URL = "http://localhost:11434/api/generate"

CACHE_DIR = "course_cache"


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def get_course_list():
    """获取课程列表"""
    response = requests.get(COURSE_LIST_URL)
    response.raise_for_status()
    return response.json()


def get_course_detail(course_id, course_number):
    """获取单个课程详情"""
    cache_path = os.path.join(CACHE_DIR, f"{course_id}.json")

    if os.path.exists(cache_path):
        print(f"课程 {course_number} 已从缓存中加载")
        with open(cache_path, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)

    url = COURSE_DETAIL_URL_TEMPLATE.format(course_id)
    response = requests.get(url)
    response.raise_for_status()
    course_detail = response.json()

    with open(cache_path, "w", encoding="utf-8") as cache_file:
        json.dump(course_detail, cache_file, ensure_ascii=False, indent=4)

    print(f"课程 {course_number} 已加载")
    return course_detail


def generate_text(prompt, model_name="llama3.1"):
    """通用的生成文本函数，调用LLM API"""
    payload = {
        "model": model_name,
        "prompt": prompt,
    }
    response = requests.post(LLAMA_API_URL, json=payload, stream=True)
    response.raise_for_status()

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


def generate_article(descriptions, model_name="llama3.1"):
    """生成阅读理解文章"""
    prompt = f'''
## Objective
I am learning English and have studied the following basic phrases and sentences: [{descriptions}]. Please generate a reading comprehension article of approximately 100 to 200 words to help me practice and improve my English. The article should primarily include the phrases and sentences I have learned. You may include a few new words or phrases to challenge me, but keep the vocabulary and sentence structures simple.

## Workflow
- Step 1: Understand the objective of the task.
- Step 2: Choose a suitable topic for the article.
- Step 3: Plan the structure of the article.
- Step 4: Write the article incorporating the learned phrases and sentences.
- Step 5: Adds minimal new vocabulary and sentence structure.
- Step 6: Finalize the article and review its content.

Take a deep breath and let’s take it step by step.

Output content does not require display steps.
    '''
    # print(prompt)
    return generate_text(prompt, model_name)


def extract_vocabulary(article, model_name="llama3.1"):
    """提取文章中的词汇表"""
    prompt = f'''
**Extract all unique words from the following English article and provide their Simplified Chinese translations and pronunciations using American pronunciation phonetics. Please format the vocabulary list as follows:**
| 单词 | 发音 | 解释 |
|------|------|------|
| Word | /pronunciation/ | Simplified Chinese translations |

### Article
{article}
    '''
    return generate_text(prompt, model_name)


def translate_article(article, model_name="llama3.1"):
    """翻译文章"""
    prompt = f'''
**Translate the following English article into clear and simplified Chinese.**

### Article
{article}
    '''
    return generate_text(prompt, model_name)


def save_to_md(directory, filename, content):
    """保存内容到Markdown文件"""
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"内容已保存到 {filepath}")


def generate_and_save_content(lesson_number, descriptions, base_dir, filename_prefix, model_name="llama3.1"):
    """生成并保存文章、词汇表和翻译"""
    print(f"正在生成课程 {lesson_number} 的文章...")
    article = generate_article(descriptions, model_name)
    print("文章生成完成。\n词汇表提取和文章翻译中...")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_vocabulary = executor.submit(extract_vocabulary, article, model_name)
        future_translation = executor.submit(translate_article, article, model_name)

        vocabulary_list = future_vocabulary.result()
        print("词汇表提取完成。")
        translation = future_translation.result()
        print("文章翻译完成。")

    content = f'''
### Vocabulary List
{vocabulary_list}

### English Article
{article}

### 中文翻译
{translation}
    '''
    save_to_md(base_dir, f"{filename_prefix}_{lesson_number}.md", content)


def main():
    ensure_cache_dir()
    course_list = get_course_list()
    courses = course_list.get("courses", [])

    if not courses:
        print("未找到任何课程。")
        return

    for index, course in enumerate(courses, start=1):
        course_title = course.get("title")
        print(f"课程编号: {index}, 标题: {course_title}")

    print("请选择一个选项:")
    print("1. Generate content for a specific lesson. \n   生成单独某一课的内容。")
    print("2. Generate content for a specific lesson and all previous lessons. \n   生成某一课及其以前的内容。")
    print("3. Generate content for all lessons and save each to a separate file. \n   生成每一课的内容并保存到对应的文件。")
    choice = input("请输入您的选择 (1/2/3): ")

    model_name = "llama3.1"

    base_dir = "generated_articles"

    if choice == '1':
        lesson_number = int(input("请输入课程的编号: "))
        selected_course = courses[lesson_number - 1]
        selected_course_id = selected_course.get("id")
        course_detail = get_course_detail(selected_course_id, lesson_number)
        statements = course_detail.get("statements", [])
        descriptions = "".join([f"({stmt['english']})、" for stmt in statements])
        generate_and_save_content(lesson_number, descriptions, os.path.join(base_dir, "specific_lesson"), "lesson", model_name)

    elif choice == '2':
        lesson_number = int(input("请输入已学到的课程编号: "))
        combined_description = ""
        for new_lesson_number in range(1, lesson_number + 1):
            course = courses[new_lesson_number - 1]
            course_id = course.get("id")
            course_detail = get_course_detail(course_id, new_lesson_number)
            statements = course_detail.get("statements", [])
            combined_description += "".join([f"({stmt['english']})、" for stmt in statements])
        generate_and_save_content(lesson_number, combined_description, os.path.join(base_dir, "up_to_lesson"), "up_to_lesson", model_name)

    elif choice == '3':
        for index, course in enumerate(courses, start=1):
            course_id = course.get("id")
            course_detail = get_course_detail(course_id, index)
            statements = course_detail.get("statements", [])
            descriptions = "".join([f"({stmt['english']})、" for stmt in statements])
            generate_and_save_content(index, descriptions, os.path.join(base_dir, "all_lessons"), "lesson", model_name)

    else:
        print("无效的选择。请重新启动程序并选择一个有效的选项。")


if __name__ == "__main__":
    main()
