from toga_cocoa.libs import NSImageScaleProportionallyUpOrDown, NSView

from .base import SimpleProbe


class BitmapViewProbe(SimpleProbe):
    native_class = NSView

    @property
    def preserve_aspect_ratio(self):
        return self.native.imageScaling == NSImageScaleProportionallyUpOrDown

    def assert_image_size(self, width, height):
        # Cocoa internally scales the image to the container,
        # so there's no image size check required.
        pass

    def get_image(self):
        image = Image.open(BytesIO(TogaImage(self.impl.get_image_data()).data))

        try:
            # If the image has an ICC profile, convert it into sRGB colorspace.
            # This is needed when attached to an laptop display; otherwise the RGB
            # values in colors in the image won't *quite* match.
            icc = image.info["icc_profile"]
            src_profile = ImageCms.ImageCmsProfile(BytesIO(icc))
            dst_profile = ImageCms.createProfile("sRGB")
            return ImageCms.profileToProfile(image, src_profile, dst_profile)
        except KeyError:
            return image
