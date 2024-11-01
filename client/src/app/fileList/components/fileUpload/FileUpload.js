"use client";
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import styles from './styles.module.css';

const FileUpload = () => {
    const [files, setFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState({});
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

        const newFiles = validFiles.map(file => ({ file, progress: 0 }));
        setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    };

    const uploadFile = async (file) => {
        const formData = new FormData();
        formData.append('files', file);

        try {
            await axios.post('http://localhost:8000/upload', formData, {
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    setUploadProgress((prevProgress) => ({
                        ...prevProgress,
                        [file.name]: percentCompleted,
                    }));
                },
            });
        } catch (error) {
            console.error(`Error uploading ${file.name}:`, error);
        }
    };

    const uploadFiles = async () => {
        if (files.length === 0) return;

        const uploadTasks = files.map(({ file }) => uploadFile(file));
        await Promise.all(uploadTasks);

        setUploadSuccess(true);
        setTimeout(() => {
            setUploadSuccess(false);
            router.push('/fileList');
        }, 2000);
    };

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: { 'text/csv': ['.csv'] },
    });

    return (
        <div>
            <div {...getRootProps({ className: styles.dropzone })}>
                <input {...getInputProps()} />
                <p>
                    Drag and drop your file(s) here, or{' '}
                    <span
                        className={styles.clickable}
                        onClick={() => document.querySelector('input[type="file"]').click()}
                    >
                        click here
                    </span>{' '}
                    to select from your system.
                </p>
            </div>
            <div className={styles.uploadButton}>
                <button className={styles.button} onClick={uploadFiles} disabled={files.length === 0}>
                    Upload
                </button>
            </div>
            {uploadSuccess && <div className={styles.snackbar}>Files successfully uploaded!</div>}

            {files.length > 0 && (
                <div>
                    <h3>Files to Upload:</h3>
                    <ul className={styles.ul}>
                        {files.map(({ file }) => (
                            <li className={styles.li} key={file.name}>
                                <span>{file.name}</span>
                                <div className={styles.progressBarContainer}>
                                    <div
                                        className={styles.progressBar}
                                        style={{ width: `${uploadProgress[file.name] || 0}%` }}
                                    ></div>
                                </div>
                                <span style={{ "marginTop": 10 }}>{uploadProgress[file.name] || 0}%</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
