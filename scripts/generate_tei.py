import sys
import os
import re
import shutil
import logging
from collections import Counter
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + '.bak')
        logging.info(f"백업 생성: {path}.bak")

def guess_title_author(text):
    # 첫 줄 제목, 두 번째 줄 저자 추정
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title = lines[0] if lines else '제목미상'
    author = lines[1] if len(lines) > 1 else '저자미상'
    return title, author

def extract_paragraphs(text):
    # 빈 줄 기준 문단 분리
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paras

def is_dialogue(para):
    # 따옴표로 시작하는 문단을 대화로 간주
    return para.startswith('"') or para.startswith("'")

def extract_person_names(paragraphs):
    # 대화 직전 문맥에서 이름 추출 (간단화)
    name_pattern = re.compile(r'([가-힣]{2,4})[가|이|은|는|이여|야|아|씨]?')
    names = []
    for i, para in enumerate(paragraphs):
        if is_dialogue(para) and i > 0:
            prev = paragraphs[i-1]
            found = name_pattern.findall(prev)
            names.extend(found)
    # 빈도순, #무명 추가
    name_counts = Counter(names)
    unique_names = [n for n, _ in name_counts.most_common()]
    if '#무명' not in unique_names:
        unique_names.append('무명')
    return unique_names

def build_tei(paragraphs, title, author, persons):
    NS = "http://www.tei-c.org/ns/1.0"
    tei = Element('TEI', xmlns=NS)
    teiHeader = SubElement(tei, 'teiHeader')
    fileDesc = SubElement(teiHeader, 'fileDesc')
    titleStmt = SubElement(fileDesc, 'titleStmt')
    SubElement(titleStmt, 'title').text = title
    SubElement(titleStmt, 'author').text = author
    SubElement(fileDesc, 'publicationStmt').text = '자동 생성'
    SubElement(fileDesc, 'sourceDesc').text = '원본: test.txt'
    profileDesc = SubElement(teiHeader, 'profileDesc')
    listPerson = SubElement(profileDesc, 'listPerson')
    for name in persons:
        SubElement(listPerson, 'person', id=f"{name}").text = name
    text_ = SubElement(tei, 'text')
    body = SubElement(text_, 'body')
    for i, para in enumerate(paragraphs):
        if is_dialogue(para):
            # 화자 추정: 직전 문단에서 이름, 없으면 무명
            speaker = '무명'
            if i > 0:
                prev = paragraphs[i-1]
                for name in persons:
                    if name in prev:
                        speaker = name
                        break
            sp = SubElement(body, 'sp', who=f"#{speaker}")
            SubElement(sp, 'speaker').text = speaker
            SubElement(sp, 'p').text = para.strip('"').strip("'")
        else:
            SubElement(body, 'p').text = para
    return tei

def main():
    if len(sys.argv) < 2:
        print("사용법: python generate_tei.py <input.txt>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = 'test_tei.xml'
    backup_file(output_path)
    with open(input_path, encoding='utf-8') as f:
        text = f.read()
    title, author = guess_title_author(text)
    paragraphs = extract_paragraphs(text)
    persons = extract_person_names(paragraphs)
    logging.info(f"제목: {title}, 저자: {author}")
    logging.info(f"등장인물: {persons}")
    tei = build_tei(paragraphs, title, author, persons)
    tree = ElementTree(tei)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    logging.info(f"TEI XML 생성 완료: {output_path}")

if __name__ == '__main__':
    main()
