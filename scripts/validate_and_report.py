import os
import subprocess
import xml.etree.ElementTree as ET
import csv
import logging

def pretty_print_xml(input_path, output_path):
    try:
        subprocess.run(["xmllint", "--format", input_path], check=True, stdout=open(output_path, 'w', encoding='utf-8'))
        return True, ""
    except Exception as e:
        return False, str(e)

def well_formed_check(input_path):
    try:
        subprocess.run(["xmllint", "--noout", input_path], check=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def relaxng_validate(input_path, rng_path):
    try:
        subprocess.run(["xmllint", "--noout", "--relaxng", rng_path, input_path], check=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def collect_stats(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    paras = root.findall('.//tei:body/tei:p', ns)
    qs = root.findall('.//tei:body/tei:q', ns)
    all_paras = paras + [p for q in qs for p in q.findall('tei:p', ns)]
    total = len(all_paras)
    dialogue = len(qs)
    narration = total - dialogue
    persons = root.findall('.//tei:listPerson/tei:person', ns)
    addressee_ptrs = root.findall('.//tei:q/tei:ptr[@type="addressee"]', ns)
    tagged_addressee = len(addressee_ptrs)
    untagged_addressee = dialogue - tagged_addressee
    return {
        '전체_문단': total,
        '대화_문단': dialogue,
        '서술_문단': narration,
        '등장인물_수': len(persons),
        '태깅된_청자': tagged_addressee,
        '미태깅_청자': untagged_addressee
    }

def write_csv(stats, output_path):
    total = stats['전체_문단']
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['항목','수량','비율'])
        writer.writerow(['전체_문단', stats['전체_문단'], '100%'])
        writer.writerow(['대화_문단', stats['대화_문단'], f"{stats['대화_문단']/total*100:.1f}%"]) 
        writer.writerow(['서술_문단', stats['서술_문단'], f"{stats['서술_문단']/total*100:.1f}%"])
        writer.writerow(['등장인물_수', stats['등장인물_수'], '-'])
        writer.writerow(['태깅된_청자', stats['태깅된_청자'], f"{stats['태깅된_청자']/stats['대화_문단']*100 if stats['대화_문단'] else 0:.1f}%"])
        writer.writerow(['미태깅_청자', stats['미태깅_청자'], f"{stats['미태깅_청자']/stats['대화_문단']*100 if stats['대화_문단'] else 0:.1f}%"])

def write_validation_log(well_formed, wf_msg, relaxng, rng_msg, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Well-formed: {'OK' if well_formed else 'FAIL'}\n{wf_msg}\n")
        f.write(f"RELAX NG: {'OK' if relaxng else 'FAIL'}\n{rng_msg}\n")

def write_readme(output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("""# TEI P5 변환 자동화 결과\n\n- 원본: test.txt\n- 1단계: test_tei.xml\n- 2단계: test_tei_with_addressee.xml\n- 3단계: test_tei_final.xml\n- 포맷팅: test_tei_final.formatted.xml\n- 품질 리포트: quality_report.csv\n- 검증 로그: validation_log.txt\n\n## 실행 명령어\n\npython scripts/generate_tei.py test.txt\npython scripts/add_addressee.py test_tei.xml\npython scripts/transform_sp_to_q.py test_tei_with_addressee.xml\nxmllint --format test_tei_final.xml > test_tei_final.formatted.xml\n\n""")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    xml_path = 'test_tei_final.xml'
    formatted_path = 'test_tei_final.formatted.xml'
    quality_csv = 'quality_report.csv'
    validation_log = 'validation_log.txt'
    readme = 'README.md'
    # Pretty-print
    pretty_ok, pretty_msg = pretty_print_xml(xml_path, formatted_path)
    # Well-formed
    wf_ok, wf_msg = well_formed_check(xml_path)
    # RELAX NG (스키마 파일 없으면 생략)
    rng_path = 'tei_all.rng'
    if os.path.exists(rng_path):
        rng_ok, rng_msg = relaxng_validate(xml_path, rng_path)
    else:
        rng_ok, rng_msg = False, '스키마 파일 없음'
    # 통계
    stats = collect_stats(xml_path)
    write_csv(stats, quality_csv)
    write_validation_log(wf_ok, wf_msg, rng_ok, rng_msg, validation_log)
    write_readme(readme)
    logging.info(f"포맷팅/검증/리포트 완료: {formatted_path}, {quality_csv}, {validation_log}, {readme}")

if __name__ == '__main__':
    main()
