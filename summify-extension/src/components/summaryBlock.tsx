import '../App.css'

interface props {
    title: string;
    text: string;
    timestamp: number;
    delay: number;
  }

  // format timestamp into minutes and seconds
  const formatTimestamp = (seconds: number) => {
    const formatString = (x: number) => {
      if (x < 10) {
        return `0${x}`
      } else {
        return `${x}`
      }
    }
    const minutes = formatString(Math.floor(seconds / 60));
    const secs = formatString(seconds % 60);
    return `${minutes}:${secs}`;
  };

  // fast forward/backward to timestamp
  const goToTimestamp = (seconds: number) => {
    // Send a message to the content script to seek to the timestamp
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs: chrome.tabs.Tab[]) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, {
          type: 'goToTimestamp',
          seconds: seconds
        });
      }
    });
  };

  const SummaryBlock: React.FC<props> = (props) => {
  return (
    <div className="card bg-gradient-to-r from-purple-500 to-cyan-400 p-1 mb-4 rounded-xl text-white text-left max-w-md shadow-lg" style={{ animationDelay: `${props.delay*0.2}s` }}>
      <div className='flex gap-2 justify-start mb-2'>
        <button onClick={() => goToTimestamp(props.timestamp)} className="inline-block border-none outline-none focus:outline-none hover:bg-black/[.4] bg-black/[.2] transition-all text-cyan-200 rounded-full px-3 py-1 h-auto text-sm font-semibold">
          {formatTimestamp(props.timestamp)}
        </button>
        <h2 className="text-lg font-semibold capitalize">{props.title}</h2>
      </div>
      <p className="text-xs text-white text-opacity-90">{props.text}</p>
    </div>
  )
}

export default SummaryBlock;