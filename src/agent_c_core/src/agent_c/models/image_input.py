import os
import base64
import logging
import tempfile
from typing import Union
from agent_c.models.base import BaseModel
from pydantic import Field, ConfigDict


class ImageInput(BaseModel):
    """
    A model to handle image input for completion calls

    Attributes:
        content_type (str): The MIME content type used to represent the image (e.g., 'image/png').
        url (Union[str, None]): Optional URL from which the image can be loaded.
        content (Union[str, None]): A base64-encoded string representing the image content.
    """
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    content_type: str = Field(..., alias="content-type")
    url: Union[str, None] = None
    content: Union[str, None] = None

    @classmethod
    def from_pil_image(cls, pil_image, filename: str = "image") -> 'ImageInput':
        """
        Creates an ImageInput instance from a Pillow (PIL) image by converting it into base64 format.

        Args:
            pil_image: The Pillow image object to convert.
            filename (str): The desired name of the file, which will be suffixed with '.png'. Default is 'image'.

        Returns:
            ImageInput: An instance of ImageInput with the image's content in base64 format.

        Raises:
            Exception: In case the image conversion process fails.

        Note:
            The image is temporarily saved as a PNG file on disk before conversion to base64, which is then removed.
        """
        temp_file_path: str = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename}.png") as temp_file:
                pil_image.save(temp_file, format="PNG")
                temp_file_path = temp_file.name

            logging.debug(f"Saved PIL image to temporary file: {temp_file_path}")

            # Read the bytes from the temporary file
            with open(temp_file_path, 'rb') as file:
                image_bytes: bytes = file.read()

            # Encode the image bytes in base64
            base64_encoded_str: str = base64.b64encode(image_bytes).decode('utf-8')

            return cls(content_type="image/png", content=base64_encoded_str, filename=f"{filename}.png")

        except Exception as e:
            logging.error(f"Failed to convert PIL image to base64: {e}")
            raise
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @classmethod
    def from_page_image(cls, page_image, filename: str = "image") -> 'ImageInput':
        """
        Generates an ImageInput instance from a page image by leveraging the `from_pil_image` method.

        Args:
            page_image: A page image object that contains an 'original' attribute with the Pillow (PIL) image.
            filename (str): The desired name of the image file. Default is 'image'.

        Returns:
            ImageInput: An ImageInput instance populated from the given page image.
        """
        return cls.from_pil_image(page_image.original, filename)

    @property
    def data_url(self) -> str:
        """
        Converts the base64-encoded image content into a data URL.

        Returns:
            str: The data URL of the image, which can be directly used in HTML.
        """
        return f"data:{self.content_type};base64,{self.content}"
