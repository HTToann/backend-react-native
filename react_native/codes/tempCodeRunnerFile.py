api_key = "AIzaSyAASMmRs9vu0Y4x84qacQGHI_ndGEtK93U"
address = "818 Nguyễn Văn Tạo,Xã Hiệp Phước, Nhà Bè, Hồ Chí Minh,Việt Nam"
full_address, latitude, longitude = get_full_address_google(address, api_key)

if full_address:
    print(f"Full Address: {full_address}")
    print(f"Latitude: {latitude}, Longitude: {longitude}")
else:
    print("Address not found")
