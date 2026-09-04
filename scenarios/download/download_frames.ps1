# Скачивает 14 кадров и 5 анимированных клипов ролика
# "Did Ancient Humans Believe in God?" и называет файлы по тайм-кодам.
#
# Как запустить (Windows PowerShell):
#   powershell -ExecutionPolicy Bypass -File download_frames.ps1
# Файлы лягут в папки .\frames и .\clips рядом со скриптом.

$B = "https://d8j0ntlcm91z4.cloudfront.net/user_3IsBFyRBGiihV2NvmAHCnNdXFA3"
New-Item -ItemType Directory -Force -Path frames, clips | Out-Null

$frames = [ordered]@{
  "0_00.png" = "hf_20260904_185228_bafbe0c3-3dd0-4751-964f-c895057a9ce6.png"
  "0_03.png" = "hf_20260904_185228_932881b5-289d-4336-b043-e058b9d6c444.png"
  "0_06.png" = "hf_20260904_185315_e9b7b1f9-e90e-4967-ad1d-7ef233f27319.png"
  "0_10.png" = "hf_20260904_185315_7c2e995f-57d1-462b-8299-2e5123a55d6f.png"
  "0_14.png" = "hf_20260904_185315_17ddc731-8273-4db8-a7b7-11f41421476b.png"
  "0_19.png" = "hf_20260904_185228_71ce401e-031b-4254-aaa4-7dc89d7c46ce.png"
  "0_24.png" = "hf_20260904_185359_767facfd-2cf7-4705-ba90-60b128ef308b.png"
  "0_29.png" = "hf_20260904_185359_c3458df7-1944-460d-955d-22d6f089ccfb.png"
  "0_34.png" = "hf_20260904_185359_1d70752f-e180-4b65-9034-b68d2bf7edd3.png"
  "0_38.png" = "hf_20260904_185439_b31c117c-7393-4463-a8e8-ff27428efd4e.png"
  "0_43.png" = "hf_20260904_185440_f3cb98b7-5477-4a58-9e51-19aaefbcbd46.png"
  "0_48.png" = "hf_20260904_185440_dda5bd3a-2603-4e96-bd9e-797234f7b4cf.png"
  "0_53.png" = "hf_20260904_185514_0cd05900-a598-44cf-ad00-1a652b48d52d.png"
  "0_57.png" = "hf_20260904_185514_1e636ce8-4851-4ba8-aee8-17098c3e89ee.png"
}
$clips = [ordered]@{
  "0_00.mp4" = "hf_20260904_190104_f666c7da-4669-4cdc-82da-b43c752c3518.mp4"
  "0_14.mp4" = "hf_20260904_190246_aca8fa04-e0cc-4d86-86d4-45026c1338cf.mp4"
  "0_24.mp4" = "hf_20260904_190103_0278cf06-6e2e-487f-88b6-73795bb72265.mp4"
  "0_43.mp4" = "hf_20260904_190245_69069f7a-0bfc-4db9-9105-4c48d3adec6e.mp4"
  "0_57.mp4" = "hf_20260904_190247_04a0efa6-d9b5-4286-a14a-19aeb4324cff.mp4"
}

Write-Host "Качаю 14 картинок в .\frames"
foreach ($k in $frames.Keys) {
  Write-Host "  $k"
  Invoke-WebRequest -Uri "$B/$($frames[$k])" -OutFile "frames\$k"
}
Write-Host "Качаю 5 клипов в .\clips"
foreach ($k in $clips.Keys) {
  Write-Host "  $k"
  Invoke-WebRequest -Uri "$B/$($clips[$k])" -OutFile "clips\$k"
}
Write-Host "Готово."
