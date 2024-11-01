"use client";
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './styles.module.css';

const FileList = () => {
    const [files, setFiles] = useState([]);
    const [previews, setPreviews] = useState({});

    useEffect(() => {
        const fetchFiles = async () => {
            try {
                const response = await axios.get('http://localhost:8000/files');
                setFiles(response.data);
            } catch (error) {
                console.error('Error fetching files:', error);
            }
        };

        fetchFiles();
    }, []);


    const fetchPreview = async (fileId, filename) => {
        try {
            const response = await axios.get(`http://localhost:8000/preview/${fileId}`);
            setPreviews((prev) => ({ ...prev, [filename]: response.data }));
        } catch (error) {
            console.error(`Error previewing file ${filename}:`, error);
        }
    };

    const downloadFile = async (id, name) => {
        try {
            const response = await axios.get(`http://localhost:8000/download/${id}`, {
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', name);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Error downloading file:', error);
        }
    };

    return (
        <div>
            <h1>Uploaded Files</h1>
            <ul className={styles.ul}>
                {files.map((file) => (
                    <li className={styles.fileTile} key={file.id}>
                        <div className={styles.fileTileHeader}>
                            <span>{file.filename}</span>
                        </div>
                        <div className={styles.fileTileButtons}>
                            <button className={styles.button} onClick={() => downloadFile(file.id, file.filename)}>Download</button>
                            <button className={styles.button} onClick={() => fetchPreview(file.id, file.filename)}>Preview</button>
                        </div>
                        {previews[file.filename] && (
                            <pre className={styles.previewBox}>{previews[file.filename].join('\n')}</pre>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default FileList;
