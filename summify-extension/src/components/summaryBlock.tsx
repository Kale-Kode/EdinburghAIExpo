import '../App.css'

interface props {
    title: string;
    text: string;
  }

  const SummaryBlock: React.FC<props> = (props) => {
  return (
    <div>
        <div className='flex space-x-8'>
            <h2>0:00</h2>
            <h2>{props.title}</h2>
        </div>
        <p>{props.text}</p>
    </div>
  )
}

export default SummaryBlock;