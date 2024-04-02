import React, { useEffect, useState } from "react"


export default function App() {

  const [data, setData] = useState([{}])

  useEffect (() => {
    fetch("/uploadedFile").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  },[])
  return (
    <div>
      
    </div>
  )
}
