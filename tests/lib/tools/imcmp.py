#!/usr/bin/env python3

# Copyright (C) 2024 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# A tool to compare images, with an optional mask isolating regions of
# interest. Input images must be of the same size and contain the same number
# of color channels. The mask is a simple B&W image, it gets reduced reduced to
# grayscale when loading and further thresholding is applied. The mask must be
# of the same pixel size as the input images. Areas blacked out in the mask are
# discarded during comparison.
import argparse
import logging

import cv2


log = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="image compare tool")
    parser.add_argument("image", nargs=2)
    parser.add_argument("--mask", help="mask to apply")
    parser.add_argument(
        "--interactive", help="show windows with images", action="store_true"
    )
    parser.add_argument("--diff-output", default="", help="save diff to this file")

    return parser.parse_args()


def main() -> None:
    opts = parse_arguments()

    im1 = cv2.imread(opts.image[0])
    im2 = cv2.imread(opts.image[1])

    log.debug("image 1 shape: %s", im1.shape)
    log.debug("image 2 shape: %s", im2.shape)

    if im1.shape != im2.shape:
        raise RuntimeError(
            "images have different shapes: img1 = {} and img2 = {}".format(
                im1.shape, im2.shape
            )
        )

    if opts.mask is not None:
        mask = cv2.imread(opts.mask, cv2.IMREAD_GRAYSCALE)
        log.debug(
            "mask grayscale %s, min %s max %s", mask.shape, mask.min(), mask.max()
        )
        # must be of the same shape as the image
        if mask.shape != im1.shape[:2]:
            raise RuntimeError(
                "mask has different shape, got {} expected {}".format(
                    mask.shape, im1.shape[:2]
                )
            )
        # apply threshold to get black & white
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        log.debug("mask %s, min %s max %s", mask.shape, mask.min(), mask.max())
    else:
        log.debug("no mask")
        mask = None

    diff_im1 = im1
    diff_im2 = im2
    if mask is not None:
        log.debug("applying mask")
        im1_masked = cv2.bitwise_and(im1, im1, mask=mask)
        im2_masked = cv2.bitwise_and(im2, im2, mask=mask)
        # when using masked, the diff is calculated between the masked images
        diff_im1 = im1_masked
        diff_im2 = im2_masked

    diff = cv2.absdiff(diff_im1, diff_im2)
    max_val = diff.max()
    log.debug("absdiff max: %s", max_val)
    if max_val == 0:
        log.debug("images are identical")
    else:
        log.debug("images are different")
        # increase the range
        diff = diff * (255.0 / diff.max())
        if opts.diff_output:
            log.debug("writing diff to %s", opts.diff_output)
            cv2.imwrite(opts.diff_output, diff)

    if opts.interactive:
        cv2.imshow("image 1", im1)
        cv2.imshow("image 2", im2)
        if mask is not None:
            cv2.imshow("mask", mask)
            cv2.imshow("image 1 masked", im1_masked)
            cv2.imshow("iamge 2 masked", im2_masked)
        cv2.imshow("diff", diff)
        cv2.waitKey()
        cv2.destroyAllWindows()

    if max_val != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
