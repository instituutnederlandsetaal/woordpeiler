import * as htmlToImage from 'html-to-image';
import { toPng, toJpeg, toBlob, toPixelData, toSvg } from 'html-to-image';
import download from 'downloadjs';

export function save() {
    const filter = (node: HTMLElement) => {
        const exclusionClasses = ['p-button'];
        return !exclusionClasses.some((classname) => node.classList?.contains(classname));
    }
    htmlToImage.toPng(document.getElementsByClassName('graph')[0])
        .then(function (dataUrl) {
            download(dataUrl, 'my-node.png');
        }).catch(function (error) {
            console.error('oops, something went wrong!', error);
        }
        );
}