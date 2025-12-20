import React, { useState, useEffect } from 'react';

const TodoList = () => {
    const [todos, setTodos] = useState([]);
    const [newTodo, setNewTodo] = useState('');

    const handleAddTodo = () => {
        setTodos([...todos, { text: newTodo, completed: false }]);
        setNewTodo('');
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewTodo(e.target.value);
    };

    useEffect(() => {
        localStorage.setItem('todos', JSON.stringify(todos));
    }, [todos]);

    return (
        <div>
            <input type="text" value={newTodo} onChange={handleInputChange} />
            <button onClick={handleAddTodo}>Add Todo</button>
            <ul>
                {todos.map((todo, index) => (
                    <li key={index}>{todo.text}</li>
                ))}
            </ul>
        </div>
    );
};

export default TodoList;
