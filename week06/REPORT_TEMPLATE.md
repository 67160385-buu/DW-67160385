# ETL Lab Report

Student ID: 67160385
Name: อัญชิสา นิยมชัย

## 1. Data Quality Problems Found
- - ข้อมูลลูกค้ามี `customer_id` ซ้ำ จึงต้องลบข้อมูลซ้ำโดยเก็บรายการแรกไว้
- ข้อมูลลูกค้าบางรายการมีค่า `province` หรือ `email` ว่าง จึงจัดการค่าที่หายไปเป็น `Unknown`
- ข้อมูลสินค้าอยู่ในรูปแบบ JSON ที่มีข้อมูลซ้อนกัน จึงต้องทำการ Flatten ข้อมูลก่อนนำไปใช้งาน
- ชื่อฟิลด์ของสินค้า เช่น `category.name` และ `pricing.price` ต้องถูกเปลี่ยนชื่อให้เหมาะสม
- ข้อมูลราคาสินค้าบางรายการอยู่ในรูปแบบข้อความและมีเครื่องหมาย comma จึงต้องแปลงเป็นตัวเลข
- ข้อมูลสินค้าบางรายการไม่มีหมวดหมู่ จึงกำหนดค่าเป็น `Unknown`
- ข้อมูลคำสั่งซื้อมี `order_id` ซ้ำ จึงต้องลบข้อมูลซ้ำ
- ข้อมูล `order_date` บางรายการไม่ถูกต้องหรือไม่สามารถแปลงเป็นวันที่ได้
- มีคำสั่งซื้อที่มี `qty <= 0`
- มีคำสั่งซื้อที่มี `unit_price <= 0`
- มีคำสั่งซื้อที่มี `discount_pct` น้อยกว่า 0 หรือมากกว่า 100
- มีคำสั่งซื้อที่อ้างอิง `customer_id` หรือ `product_id` ที่ไม่มีอยู่ในข้อมูล Master
- คำสั่งซื้อบางรายการมีสถานะเป็น `pending` หรือ `cancelled` ซึ่งไม่ถูกนำมาคำนวณยอดขาย เนื่องจาก Pipeline กำหนดให้ใช้เฉพาะสถานะ `paid` และ `completed`

## 2. Cleaning / Transformation Rules
- ลบข้อมูลลูกค้าที่มี `customer_id` ซ้ำ โดยเก็บข้อมูลรายการแรกไว้ จากนั้นทำการ Standardize ค่า `province` และจัดการค่า `province` และ `email` ที่หายไปโดยกำหนดเป็น `Unknown`
- ทำการ Flatten ข้อมูล JSON ที่มีโครงสร้างซ้อนกันด้วย `json_normalize()` จากนั้นเปลี่ยนชื่อฟิลด์ดังนี้
- `category.name` → `category`
- `pricing.price` → `price`
- นอกจากนี้แปลงข้อมูล `price` ให้เป็นชนิดตัวเลข และกำหนดค่า `category` ที่หายไปเป็น `Unknown`
- ลบข้อมูล `order_id` ที่ซ้ำกัน แปลง `order_date` ให้เป็นรูปแบบวันที่ และปรับสถานะของคำสั่งซื้อให้อยู่ในรูปแบบตัวพิมพ์เล็ก

จากนั้นตรวจสอบข้อมูลที่ไม่ถูกต้อง
- `qty <= 0`
- `unit_price <= 0`
- `discount_pct < 0`
- `discount_pct > 100`
- `order_date` ไม่ถูกต้อง

ข้อมูลที่ไม่ผ่านเงื่อนไขจะถูกแยกออกไปเก็บในไฟล์ `rejects.csv`
สำหรับคำสั่งซื้อที่ผ่านการตรวจสอบ จะเก็บเฉพาะสถานะ `paid` และ `completed`

- คำนวณยอดขายตามสูตร
`gross_amount = qty × unit_price`
`discount_amount = gross_amount × discount_pct / 100`
`sales_amount = gross_amount - discount_amount`

## 3. Rejected Records
จำนวน: 4 รายการ

เหตุผลหลัก:   
1.O0007: จำนวนสั่งซื้อติดลบ (qty = -2) -> Invalid Record Rules
2.O0021: ส่วนลดเกิน 100% (discount_pct = 150) -> Invalid Record Rules
3.O0034: รูปแบบวันที่ไม่ถูกต้อง (order_date = 'not-a-date') -> Invalid Record Rules
4.O0091: ราคาต่อหน่วยติดลบ (unit_price = -100.0) -> Invalid Record Rules

## 4. ETL Validation
- Valid transformed rows: 16 รายการ
- Warehouse rows: 16 รายการ
- Duplicate order_id: 0 รายการ
- Source total sales: 22022.66 บาท
- Warehouse total sales: 22022.66 บาท
- Validation status: จำนวนแถวและยอดขายรวมใน Warehouse ตรงกับ ข้อมูลที่ผ่านการ Transformแล้ว

## 5. Idempotency Test
จำนวน fact_sales หลัง run ครั้งที่ 1: 16 รายการ
จำนวน fact_sales หลัง run ครั้งที่ 2: 16 รายการ

อธิบายผล:ระบบ ETL มีคุณสมบัติ Idempotency เนื่องจากเมื่อทำการสั่งรัน Pipeline ซ้ำเป็นครั้งที่ 2 ด้วยข้อมูลชุดเดิม ระบบทำการเขียนทับ/อัปเดตข้อมูลเดิมได้อย่างถูกต้อง (เช่น การใช้ if_exists='replace' หรือ UPSERT) ส่งผลให้จำนวนแถวในตาราง fact_sales ยังคงเป็น 100 รายการ และยอดขายรวมคงที่ที่ 22022.66 บาท เท่าเดิม ไม่เกิดการสร้างข้อมูลซ้ำซ้อนหรือทำให้ยอดขายเพิ่มขึ้นผิดปกติ
