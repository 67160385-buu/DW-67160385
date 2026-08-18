วิธีการติดตั้งและการเตรียมระบบ (Installation & Setup)
1. ความต้องการของระบบ (Prerequisites)
Python: เวอร์ชัน 3.8 ขึ้นไป
SQLite3: ติดตั้งมาพร้อมกับ Python Standard Library
2. การติดตั้ง Dependencies
เปิด Terminal / Command Prompt ในโฟลเดอร์โปรเจกต์ แล้วรันคำสั่ง:
```bash
pip install pandas numpy openpyxl
```
วิธีการรัน Pipeline
1.การรันผ่าน Python Script (`pipeline.py`)
วางไฟล์ `Python_Data_Pipeline_Lab_Dataset (1).xlsx` ไว้ในโฟลเดอร์เดียวกับ `pipeline.py` แล้วรันคำสั่ง:
```bash
python pipeline.py
```
ผลลัพธ์หลังการรัน:
> ระบบจะสร้างฐานข้อมูล `retail_dw.db` ขึ้นมาอัตโนมัติ
> ระบบจะส่งออกไฟล์ `quarantine.csv` และ `pipeline_run_log.csv` สรุปผลการประมวลผล

โครงสร้าง Star Schema
1. Fact Table (fact_sales)
order_id (Primary Key, รหัสคำสั่งซื้อที่อัปเดตล่าสุด)
date_key, customer_key, product_key (Foreign Keys เชื่อมไปยัง Dimension)
quantity, unit_price, discount_pct
gross_amount (ยอดก่อนหักส่วนลด), net_amount (ยอดสุทธิ)
payment_method, sales_channel

2. Dimension Tables
dim_customer: customer_key (PK), customer_id, customer_name, province, segment
dim_product: product_key (PK), product_id, product_name, category
dim_date: date_key (PK), full_date, day, month, quarter, year

คำตอบ Reflection
1. ความท้าทายหลักในการทำ Data Pipeline และแนวทางการแก้ไข
คุณภาพข้อมูลที่ไม่สมบูรณ์ (Data Quality Issues): ข้อมูลต้นทางอาจมีค่าว่าง, รูปแบบวันที่ผิดพลาด หรือการอ้างอิงรหัสสินค้า/ลูกค้าที่ไม่มีอยู่จริง
แนวทางแก้ไข*: ออกแบบ Validation Framework เพื่อกรองและกักข้อมูลที่ไม่ผ่านเงื่อนไขลงตาราง/ไฟล์ Quarantine ช่วยให้กระบวนการ ETL ทำงานได้อย่างราบรื่นโดยไม่ล่มกลางทาง (Fault Tolerance)
การรักษาความถูกต้องของข้อมูล (Data Consistency): การคำนวณ `gross_amount` และ `net_amount` ต้องมีความแม่นยำสูง
แนวทางแก้ไข: คำนวณยอดขายสุทธิตามหลักคณิตศาสตร์และปรับเศษทศนิยมตามมาตรฐานการเงินก่อนบันทึกลง Data Warehouse
2. ข้อดีของการออกแบบ Data Warehouse แบบ Star Schema
ประสิทธิภาพการดึงข้อมูล (Query Performance): การเชื่อมตารางด้วย Surrogate Keys ระหว่าง Fact Table และ Dimension Tables ทำให้ลดการทำ Complex Join ได้อย่างมาก
ใช้งานง่ายกับ BI Tools: ช่วยให้ผู้ใช้ฝั่งวิเคราะห์ หรือเครื่องมือ Visualization (เช่น Power BI, Tableau) สามารถเข้าใจโครงสร้างและสร้างรายงานวิเคราะห์ได้ง่าย
3. ข้อเสนอแนะในการพัฒนาต่อ่อย (Future Improvements)
การทำ Orchestration: นำ Apache Airflow หรือ Prefect เข้ามาจัดเวลาและกำหนด Workflow การประมวลผลอัตโนมัติ
SCD (Slowly Changing Dimensions): พัฒนา `dim_customer` หรือ `dim_product` รองรับ SCD Type 2 เพื่อบันทึกประวัติการเปลี่ยนแปลงตามช่วงเวลา (Historical Tracking)
