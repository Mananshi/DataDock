"use client";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}`, {
          method: "GET"
        });
        const data = await response.json();
        setMessage(data.message);
      } catch (error) {
        console.error("Error fetching message:", error);
      }
    };
    fetchMessage();
  }, []);

  return <div className="text-center mt-4 text-xl">{message}</div>;
}
