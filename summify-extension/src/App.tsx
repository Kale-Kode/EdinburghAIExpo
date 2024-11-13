import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import { useEffect, useState } from 'react';
import './App.css'
import SummaryBlock from './components/summaryBlock';
import Lottie from 'lottie-react';
import Loading from './assets/loading.json'

// define types to prevent unknown type errors later
interface SummaryItem {
  title: string;
  text: string;
}

function App() {

  // STATES

  const [url, setUrl] = useState('');
  const [onYtVideo, setOnYtVideo] = useState(false);
  const [summary, setSummary] = useState<SummaryItem[]>([]);


  // BROWSER ACTIONS

  // Get the active tab URL
  const getCurrentTabUrl = async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.url) {
        setUrl(tab.url);
      }
    } catch (error) {
      console.error('Error retrieving tab URL:', error);
    }
  };

  // Check if the current URL is a YouTube video
  useEffect(() => {
    if (url.includes("youtube.com/watch")) {
      setOnYtVideo(true);
      fetchSummary(); // Fetch summary
    } else {
      setOnYtVideo(false);
    }
  }, [url]);

  // Fetch the current tab URL when the component mounts
  useEffect(() => {
    getCurrentTabUrl();
    localStorage.setItem('videoUrl', JSON.stringify(url))
    console.log(url)
  }, []);


  // SUMMARY FETCHING AND STORING

  // Check if summary is in localStorage
  const summaryInCache = () => {
    const cachedSummary = localStorage.getItem('videoSummary'); // Retrieve cached summary
    const video_url = localStorage.getItem('videoUrl'); // Retrieve the relevant video url to identify the summary
    if (cachedSummary && video_url == url) { // if stored summary is or the current video, use it
      return JSON.parse(cachedSummary); // Return parsed summary
    }
    return null; // Otherwise, no cached summary found
  };

  // Fetch summary from API
  const fetchSummary = async () => {
    console.log("fetching summary")
    const cachedSummary = summaryInCache();
    // use cached summary if it's stored
    if (cachedSummary) {
      setSummary(cachedSummary)
    } else {
      // otherwise generate from API
      try {
        const response = await fetch('http://127.0.0.1:5000/summarise', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ video_url: url }), // Sending the video URL in the request body
        });
    
        if (!response.ok) {
          throw new Error('Failed to fetch summary');
        }
    
        const data = await response.json();
        
        if (Array.isArray(data.summary)) {
          localStorage.setItem('videoSummary', JSON.stringify(data.summary));
          localStorage.setItem('videoUrl', JSON.stringify(url));
          setSummary(data.summary);
  
        } else {
          console.error('Invalid response format:', data);
          setSummary([]);
        }
  
      } catch (error) {
        console.error('Error fetching summary:', error);
        setSummary([]);
      }

    }
  }

  // summary debug
  useEffect(() => {
    console.log(summary)
  }, [summary])

  // Render summary chunk components
  const renderSummary = () => {
    return (
      <>
        <h1 className=''>Video summary:</h1>
        {
          summary.map((content, i) => {
            <SummaryBlock title={content.title} text={content.text} key={i}/>
          })
        }
      </>
    );
  };

  return (
    <>
      {onYtVideo ? (
        summary.length > 0 ? (
          renderSummary()
        ) : (
          <div>
            <h3>Generating summary (please keep this popup open)</h3>
            <Lottie loop={true} animationData={Loading}></Lottie>
          </div>
        )
      ) : (
        <p>Watch a YouTube video to get a summary.</p>
      )}

      <div className='flex justify-center'>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
    </>
  )
}

export default App
