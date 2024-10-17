from typing import List

import numpy as np
from PIL import Image
from PIL.Image import Image as PILImage

from .base import BaseSession


class SiluetaSession(BaseSession):
    """This is a class representing a SiluetaSession object."""

    def predict(self, img: PILImage, *args, **kwargs) -> List[PILImage]:
        """
        Predict the mask of the input image.

        This method takes an image as input, preprocesses it, and performs a prediction to generate a mask. The generated mask is then post-processed and returned as a list of PILImage objects.

        Parameters:
            img (PILImage): The input image to be processed.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            List[PILImage]: A list of post-processed masks.
        """
        ort_outs = self.inner_session.run(
            None,
            self.normalize(
                img, (0.485, 0.456, 0.406), (0.229, 0.224, 0.225), (320, 320)
            ),
        )

        pred = ort_outs[0][:, 0, :, :]

        ma = np.max(pred)
        mi = np.min(pred)

        pred = (pred - mi) / (ma - mi)
        pred = np.squeeze(pred)

        mask = Image.fromarray((pred * 255).astype("uint8"), mode="L")
        mask = mask.resize(img.size, Image.Resampling.LANCZOS)

        return [mask]

    @classmethod
    def download_models(cls, *args, **kwargs):
        """
        Download the pre-trained model file.

        This method downloads the pre-trained model file from a specified URL. The file is saved to the U2NET home directory.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str: The path to the downloaded model file.
        """
        return kwargs["offline_model_path"]

    @classmethod
    def name(cls, *args, **kwargs):
        """
        Return the name of the model.

        This method returns the name of the Silueta model.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str: The name of the model.
        """
        return "silueta"
