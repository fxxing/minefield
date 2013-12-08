import subprocess

TEXTURE_FORMATS = {"png": "png", "pvr2": "pvr", "pvr2gz": "pvr.gz", "pvr2ccz": "pvr.ccz", "jpg": "jpg", "bmp": "bmp",
                   "tga": "tga", "tiff": "tiff", "pkm": "pkm", "ppm_ascii": "ppm", "ppm_binary": "ppm"}
IMAGE_FORMATS = ["RGBA8888", "BGRA8888", "RGBA4444", "RGBA5555", "RGBA5551", "RGB888", "RGB565", "PVRTC4", "PVRTC2",
                 "PVRTC2_NOALPHA", "PVRTC4_NOALPHA", "ALPHA", "ALPHA_INTENSITY", "ETC1"]

CMD = "TexturePacker --data out/%(texture_format)s_%(image_format_name)s.plist" \
      " --sheet out/%(texture_format)s_%(image_format_name)s.%(image_ext)s" \
      " --texture-format %(texture_format)s --opt %(image_format)s" \
      " --format cocos2d --force-publish --algorithm MaxRects" \
      " --maxrects-heuristics Best --size-constraints AnySize --pack-mode Best --png-opt-level 0 textures/*.png"


def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
    output = process.communicate()
    retcode = process.poll()
    if retcode:
        print output


def create_all():
    for texture_format in TEXTURE_FORMATS:
        for image_format in IMAGE_FORMATS:
            # PVRTC only support pvr
            if "PVRTC" in image_format and "pvr" not in texture_format:
                continue
            # ETC1 only support pkm
            if "ETC1" == image_format and "pkm" != texture_format:
                continue
            # ALPHA_INTENSITY cannot be used with png/jpg/bmp
            if "ALPHA_INTENSITY" == image_format and texture_format in ("png", "jpg", "bmp"):
                continue
            # RGBA5555 not supported by pvr exporter
            if "RGBA5555" == image_format and "pvr" in texture_format:
                continue
            cmd = CMD % {"texture_format": texture_format,
                         "image_format": image_format,
                         "image_format_name": image_format.lower(),
                         "image_ext": TEXTURE_FORMATS[texture_format]}
            run_cmd(cmd)
    tea_cmd = CMD % {"texture_format": "pvr2ccz",
                     "image_format": "RGBA8888",
                     "image_format_name": "rgba8888_tea",
                     "image_ext": 'pvr.ccz'}
    tea_cmd += " --content-protection aaaaaaaabbbbbbbbccccccccdddddddd"
    run_cmd(tea_cmd)


if __name__ == "__main__":
    create_all()