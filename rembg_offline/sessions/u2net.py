from typing import List

import numpy as np
from PIL import Image
from PIL.Image import Image as PILImage

from .base import BaseSession


class U2netSession(BaseSession):
    """
    This class represents a U2net session, which is a subclass of BaseSession.
    """

    def predict(self, img: PILImage, *args, **kwargs) -> List[PILImage]:
        """
        Predicts the output masks for the input image using the inner session.

        Parameters:
            img (PILImage): The input image.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            List[PILImage]: The list of output masks.
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
        Downloads the U2net model file from a specific URL and saves it.

        Parameters:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The path to the downloaded model file.
        """
        return kwargs["offline_model_path"]

    @classmethod
    def name(cls, *args, **kwargs):
        """
        Returns the name of the U2net session.

        Parameters:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The name of the session.
        """
        return "u2net"
