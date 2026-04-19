# Daily Practice — Cách luyện mỗi ngày

## Nguyên tắc

> **Học lập trình như học ngoại ngữ: ít mà đều > nhiều mà ngắt quãng.**

- 30 phút đều đặn > 3 giờ cuối tuần
- Gõ tay > copy paste
- Build > đọc
- Giải thích lại cho người khác (hoặc rubber duck) > chỉ hiểu trong đầu

## Lịch ngày

### Ngày làm bài tập (4-5 ngày/tuần)
- **5 phút** — review code hôm qua, `git diff`, commit
- **30-45 phút** — làm exercise mới
- **10 phút** — viết lại 1-2 câu ghi nhớ khái niệm mới học

### Ngày review (1-2 ngày/tuần)
- **30 phút** — đọc lại code tuần rồi, refactor chỗ nào thấy xấu
- **30 phút** — giải thích lại khái niệm khó cho bản thân bằng lời

### Ngày build (1 ngày/tuần)
- **1-2 giờ** — tập trung vào mini-project phase hiện tại

## Workflow mỗi buổi code

1. `git pull` / check lại mình đang ở đâu (mở PHASE.md)
2. Tạo branch hoặc tiếp tục branch đang làm
3. Đọc exercise → **nghĩ 2 phút trước khi gõ** (quan trọng)
4. Gõ tay, chạy thử, fix lỗi
5. Commit khi xong 1 bài (commit nhỏ tốt hơn ít mà to)
6. Lùi lại, đọc code vừa viết — có chỗ nào tự hỏi "sao mình viết thế?"
7. 10 phút cuối: note ra 1-2 insight vào `NOTES.md` của phase

## Template ghi chú mỗi phase

Tạo file `NOTES.md` trong mỗi phase với cấu trúc:

```markdown
# Phase X — Notes

## Tuần 1

### Hôm nay học gì
- ...

### Cái gì khó
- ...

### "Aha moment"
- ...

### Câu hỏi chưa trả lời được
- ...
```

Câu hỏi để sau review lại. Thường tuần sau đã trả lời được.

## Khi bạn stuck

### Rule 30-30-30
1. **30 phút tự vật lộn** — đừng google ngay
2. **30 phút google + docs** — tìm người khác gặp chưa
3. **30 phút hỏi AI / cộng đồng** — trình bày đầy đủ context

Nếu vẫn chưa xong sau 90 phút → nghỉ, làm bài khác, mai quay lại. Não cần thời gian.

### Template hỏi
```
Tôi đang cố [mục tiêu]
Tôi đã thử [X, Y, Z] nhưng gặp [error message cụ thể]
Code của tôi: [minimal reproducible example]
Kỳ vọng: ..., thực tế: ...
Môi trường: Python 3.X, FastAPI 0.X, OS...
```

Hỏi tốt = giải quyết 50% vấn đề.

## Rubber duck debugging

Khi stuck, **nói chuyện** với con vịt cao su (hoặc ChatGPT):
1. Mô tả vấn đề bằng lời
2. Giải thích từng bước code
3. Bạn sẽ tự phát hiện bug ở đâu

~70% bug tự nghe ra khi phải nói thành lời.

## Đo tiến độ

### Tuần
- Đã hoàn thành phase/ngày theo kế hoạch chưa?
- Code viết ra có "hiểu được" sau 1 tuần không?
- Có thấy khái niệm cũ thành "quen" chưa?

### Tháng
- Có thể build project tương đương phase gần nhất **không cần xem** PHASE.md?
- Debug lỗi đã quen hơn chưa (nhìn traceback đoán được)?
- Viết test thấy tự nhiên chưa?

Nếu "không" cho ≥ 2 câu → nên ôn lại phase đó, đừng bỏ qua.

## Motivation khi đuối

- **Ghi lại** tuần đầu bạn viết gì, tuần này viết gì. So sánh → thấy tiến bộ
- **Share** code lên GitHub — người khác thấy → motivated hơn
- **Tìm nhóm** học cùng (Discord, Reddit, bạn bè)
- **Build** thứ bạn sẽ dùng thật, không phải demo nhạt nhẽo

## Pitfall thường gặp khi self-study

### ❌ "Tutorial hell"
Xem/đọc hết tutorial này tới tutorial khác mà không build.
→ Fix: cứ xong 1 concept là build thứ gì đó áp dụng ngay, dù nhỏ.

### ❌ Perfectionism
"Code chưa đẹp, chưa deploy được, chưa dám push."
→ Fix: `git init` + commit "first commit, ugly but works". Sẽ đẹp sau.

### ❌ Jump ahead
"Chưa test ổn nhưng muốn học microservices luôn"
→ Fix: tuân theo thứ tự phase. Skip ≠ nhanh, thường là chậm hơn vì phải quay lại.

### ❌ Chỉ học, không thực hành
"Đọc sách nào về SQLAlchemy hay nhất?"
→ Fix: mở psql lên gõ CREATE TABLE. Đọc sau.

### ❌ Không commit / không push
Code trên máy → 1 ngày nào đó mất sạch.
→ Fix: `git commit` mỗi lần xong 1 exercise, push lên GitHub cuối ngày.

## Tips thực tế

- **Pomodoro** 25p code + 5p nghỉ — giữ focus
- **Đừng code sau 10h đêm** — bug viết đêm = bug sáng phải debug
- **Giữ environment setup đơn giản** — đừng nerd-snipe vào cấu hình editor
- **Code trên máy khác được** — sync qua git, đừng rely vào 1 máy

## Mỗi tuần tự hỏi

1. Tuần này mình học được 1 concept mới nào?
2. Mình đã áp dụng concept đó vào code thật chưa?
3. Có chỗ nào mình còn confused, cần ôn không?
4. Tuần sau mình sẽ làm gì cụ thể?

Viết vào journal. Không cần dài. 10 phút mỗi chủ nhật.

## Chúc bạn học bền bỉ

> "The best time to plant a tree was 20 years ago. The second best time is now."

Đừng so sánh với người khác. So sánh với mình tuần trước.
