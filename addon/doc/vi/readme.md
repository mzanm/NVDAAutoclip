# Tiện ích NVDA Autoclip

Tiện ích NVDA Autoclip tự động đọc nội dung của bộ nhớ tạm bất cứ khi nào nó thay đổi. Điều này có thể hữu ích nếu bạn chơi trò chơi xuất văn bản vào bộ nhớ tạm và không hỗ trợ xuất trực tiếp ra NVDA. Không cần chương trình bên ngoài để sử dụng tiện ích bổ sung này

[Nhật ký thay đổi](https://github.com/mzanm/NVDAAutoclip/blob/main/changelog.md)
[Tải xuống phiên bản mới nhất](https://github.com/mzanm/NVDAAutoclip/releases/latest/download/Autoclip.nvda-addon)

## Cài đặt

**Khả năng tương thích:** NVDA 2021.1 hoặc cao hơn

**Lưu ý:** Tiện ích bổ sung này có sẵn trong cửa hàng tiện ích bổ sung của NVDA (menu NVDA > công cụ > Cửa hàng tiện ích bổ sung > tab Tiện ích bổ sung có sẵn), sau đây là hướng dẫn cài đặt thủ công.

1. Tải xuống bản phát hành mới nhất từ ​​[trang phát hành](https://github.com/mzanm/NVDAAutoclip/releases) hoặc liên kết tải xuống trực tiếp ở trên.

2. Nhấp vào tệp tải xuống trong khi NVDA đang chạy và hộp thoại cài đặt tiện ích bổ sung sẽ xuất hiện.

## Cách sử dụng

Sau khi tiện ích bổ sung được cài đặt và bật thông qua phím tắt hoặc tùy chọn trong menu công cụ, tiện ích này sẽ tự động đọc nội dung của bộ nhớ tạm bất cứ khi nào nó thay đổi. Lưu ý rằng theo mặc định, tiện ích bổ sung được kích hoạt tạm thời cho đến lần khởi động lại NVDA tiếp theo. Tiện ích bổ sung không lưu trạng thái của nó trong cấu hình của NVDA trừ khi bạn thay đổi hành vi đó trong phần cài đặt của tiện ích bổ sung:

### Bật/Tắt

- **Phím tắt**: Nhấn `NVDA+Control+Shift+K` để chuyển đổi chế độ đọc bộ nhớ tạm tự động. Phím tắt có thể được gán lại trong hộp thoại thao tác nhập NVDA bình thường như tất cả các thao tác khác. Nó có thể được tìm thấy trong danh mục Autoclip.
- **Menu công cụ**: Mở menu công cụ NVDA và chọn "`Đọc bộ nhớ tạm tự động`" để bật hoặc tắt.

## Cấu hình

Truy cập cài đặt thông qua hộp thoại Cài đặt NVDA > danh mục Autoclip.

- **Ngắt trước khi đọc bộ nhớ tạm**: Có nên ngắt lời nói hiện tại trước khi đọc thay đổi bộ nhớ tạm hay không
- **Ghi nhớ tự động đọc bộ nhớ tạm sau khi khởi động lại NVDA**: Duy trì trạng thái bật/tắt khi khởi động lại (bắt buộc đối với hồ sơ cấu hình)
- **Hiển thị trong menu công cụ của NVDA**: Chuyển đổi chế độ hiển thị trong menu Công cụ

#### Cài đặt nâng cao

- **Chia văn bản trên độ dài này thành các phân đoạn được nói riêng**: Số ký tự tối đa trên mỗi phân đoạn để không lấn át bộ tổng hợp giọng nói khi một khối văn bản lớn được sao chép vào bộ nhớ tạm (mặc định: 500, đặt dưới 100 để tắt hoàn toàn tính năng chia tách văn bản)
- **Cố gắng phân tách các đoạn ở ranh giới từ**: Khi bật tính năng chia tách văn bản, hãy phân tách ở các khoảng trắng để tránh cắt các từ (mặc định: đã bật)
- **Độ dài văn bản tối đa để nói**: Bỏ qua các bản cập nhật bộ nhớ tạm vượt quá độ dài này (mặc định: 15.000 ký tự)
- **Độ trễ gỡ lỗi**: Ngăn chặn việc lặp lại nội dung giống hệt nhau trong khoảng thời gian trễ này tính bằng mili giây (mặc định: 100 mili giây, 0 để tắt, -1 nếu không bao giờ trùng lặp)
- **Độ trễ tối thiểu giữa các lần ngắt giọng nói**: mili giây tối thiểu giữa các lần ngắt khi tính năng ngắt được bật (mặc định: 50 mili giây, 0 để luôn ngắt)
- **Khôi phục mặc định**: Đặt lại tất cả cài đặt nâng cao
