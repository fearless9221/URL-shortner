import { useState } from "react";

function ListGroup(){
    const items = ['New York', 'San Francisco', 'Tokyo', 'London', 'Paris'];
    const message=items.length === 0 && <p>No items found</p>
    const [SelectedIndex, setSelectedIndex] = useState(-1);
    return (
        <ul className="list-group">
            <h1>List Group</h1>
            {message}
            {items.map((item,index) => <li key={item} onClick={() => setSelectedIndex(index)} className={SelectedIndex === index ? 'list-group-item active' : 'list-group-item'}>{item}</li>)}
        </ul>
    )
}
export default ListGroup