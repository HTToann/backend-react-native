import requests


def get_location_from_maps(address):
    try:
        key = "xKb2q5zsUSD3ImAG0qqIgNDPT0gZ2nSrcFU0nGQyyaMpUKdjoZeU1pVl9AOqixUI"
        url = "https://api.distancematrix.ai/maps/api/geocode/json"
        params = {"address": address, "key": key, "language": "vi"}

        # Gửi yêu cầu HTTP
        response = requests.get(url, params=params)

        # Kiểm tra mã trạng thái HTTP
        response.raise_for_status()  # Kiểm tra nếu có lỗi HTTP (400, 404, 500,...)

        # Phân tích JSON trả về
        data = response.json()

        # Kiểm tra nếu status = OK
        if data.get("status") == "OK":
            location = data["result"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print(
                "Error:",
                data.get("status", "Unknown status"),
                data.get("error_message", ""),
            )
            return None, None
    except requests.exceptions.RequestException as e:
        # Bắt lỗi nếu có vấn đề với yêu cầu HTTP (lỗi kết nối, time out, v.v.)
        print(f"HTTP Request error: {e}")
        return None, None
    except KeyError as e:
        # Bắt lỗi nếu không thể tìm thấy key trong phản hồi JSON
        print(f"KeyError: Missing key {e} in the response data")
        return None, None
    except Exception as e:
        # Bắt lỗi chung cho mọi lỗi khác
        print(f"An unexpected error occurred: {e}")
        return None, None


# address = "16 Đoàn Nguyễn Tuấn, Tân Quý Tây, Bình Chánh, Hồ Chí Minh, Việt Nam"
# latitude, longitude = get_location_from_maps(address)

# if latitude and longitude:
#     print(f"Tọa độ của địa chỉ '{address}':")
#     print(f"Vĩ độ: {latitude}")
#     print(f"Kinh độ: {longitude}")
# else:
#     print("Không thể lấy tọa độ cho địa chỉ này.")
