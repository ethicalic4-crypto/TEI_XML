# TEI P5 변환 자동화 결과

- 원본: test.txt
- 1단계: test_tei.xml
- 2단계: test_tei_with_addressee.xml
- 3단계: test_tei_final.xml
- 포맷팅: test_tei_final.formatted.xml
- 품질 리포트: quality_report.csv
- 검증 로그: validation_log.txt

## 실행 명령어

python scripts/generate_tei.py test.txt
python scripts/add_addressee.py test_tei.xml
python scripts/transform_sp_to_q.py test_tei_with_addressee.xml
xmllint --format test_tei_final.xml > test_tei_final.formatted.xml

