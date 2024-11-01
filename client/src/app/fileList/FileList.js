"use client";
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './styles.module.css';

const FileList = () => {
    const [files, setFiles] = useState([]);

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
            <ul className={styles.fileList}>
                {files.map((file) => (
                    <li>
                        <span>{file.filename}</span>
                        <button onClick={() => downloadFile(file.id, file.filename)}>Download</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default FileList;
