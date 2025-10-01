import sys
import os
import re
import shutil
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + '.bak')
        logging.info(f"백업 생성: {path}.bak")

def extract_persons(tree):
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    persons = {}
    for p in tree.findall('.//tei:listPerson/tei:person', ns):
        pid = p.attrib.get('id')
        persons[pid] = p.text
    return persons

def find_addressee(text, persons):
    # 직접 호명: 이름+야/아/씨
    for pid, name in persons.items():
        if not name or name == '무명':
            continue
        if re.search(rf'{re.escape(name)}[야아씨]', text):
            return pid
    return None

def main():
    if len(sys.argv) < 2:
        print("사용법: python add_addressee.py <input.xml>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = 'test_tei_with_addressee.xml'
    backup_file(output_path)
    tree = ET.parse(input_path)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    persons = extract_persons(tree)
    prev_speaker = None
    tagged = 0
    untagged = 0
    for sp in root.findall('.//tei:sp', ns):
        who = sp.attrib.get('who', '#무명').lstrip('#')
        p = sp.find('tei:p', ns)
        if p is not None:
            addressee = find_addressee(p.text or '', persons)
            if not addressee:
                # 문맥 추론: 이전 화자
                addressee = prev_speaker if prev_speaker and prev_speaker != who else None
            if addressee:
                ptr = ET.Element('ptr', {'type': 'addressee', 'target': f'#{addressee}'})
                sp.insert(0, ptr)
                tagged += 1
            else:
                untagged += 1
        prev_speaker = who
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    logging.info(f"청자 태깅 완료: {output_path} (tagged: {tagged}, untagged: {untagged})")

if __name__ == '__main__':
    main()
