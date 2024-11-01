"use client";
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import styles from './styles.module.css';

const FileUpload = () => {
    const [files, setFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadSuccess, setUploadSuccess] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();

    const onDrop = (acceptedFiles) => {
        const validFiles = acceptedFiles.filter(file => file.name.endsWith('.csv'));
        const invalidFiles = acceptedFiles.filter(file => !file.name.endsWith('.csv'));

        if (invalidFiles.length > 0) {
            setError('Only .csv files are allowed!');
        } else {
            setError('');
        }

        setFiles((prevFiles) => [...prevFiles, ...validFiles]);
    };

    const uploadFiles = async () => {
        if (files.length === 0) return;

        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files', file);
        });

        try {
            await axios.post('http://localhost:8000/upload', formData, {
                onUploadProgress: (progressEvent) => {
                    const total = progressEvent.total;
                    const current = progressEvent.loaded;
                    setUploadProgress(Math.round((current / total) * 100));
                },
            });
            setUploadSuccess(true);
            setFiles([]);
            setTimeout(() => {
                setUploadSuccess(false);
                router.push('/fileList');
            }, 2000);
        } catch (error) {
            console.error('Error uploading files:', error);
        }
    };

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: { 'text/csv': ['.csv'] },
    });

    return (
        <div>
            <div {...getRootProps({ className: styles.dropzone })}>
                <input {...getInputProps()} />
                <p>Drag and drop your file(s) here, or <span className={styles.clickable} onClick={() => document.querySelector('input[type="file"]').click()}>click here</span> to select from your system.</p>
            </div>
            <button onClick={uploadFiles} disabled={files.length === 0}>
                Upload
            </button>
            {uploadProgress > 0 && <div>Progress: {uploadProgress}%</div>}
            {uploadSuccess && <div className={styles.snackbar}>Files successfully uploaded!</div>}

            {files.length > 0 && (
                <div>
                    <h3>Files to Upload:</h3>
                    <ul>
                        {files.map((file) => (
                            <li key={file.name}>{file.name}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
