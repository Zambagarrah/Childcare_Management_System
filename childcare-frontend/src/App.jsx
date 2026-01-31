import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [status, setStatus] = useState("");

  useEffect(() => {
    axios.get("http://localhost:8000/api/health/")
      .then(res => setStatus(res.data.status))
      .catch(err => {
        console.error(err);
        setStatus("error");
      });
  }, []);

  return (
    <div className="container mt-5">
      <h1 className="text-center">Backend Status: {status}</h1>
    </div>
  );
}

export default App;
