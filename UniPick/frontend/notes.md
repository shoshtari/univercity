# These are the things I learned by doing frontend of this project

## Usestate

assume we want a counter. with plain js, we would have something like this:

```
<p id="count">0</p>
<button onclick="increment()">+</button>

<script>
  let count = 0;

  function increment() {
    count++;
    document.getElementById("count").innerText = count;
  }
</script>
```

we store the value in a variable and each time the button is clicked we update its state.
using react, we can do something like this:

```
function App() {
  const [count, setCount] = useState(0);

  function increment() {
    setCount(count + 1);
  }

  return (
    <div>
      <p>{count}</p>
      <button onClick={increment}>+</button>
    </div>
  );
}
```

`useState` store value between renders.

## preventDefault

when using forms, default actions in JS are not suitable for react. for example in default, it reload the page but react is a single page app and we don't want that so we do forms like this:

```
function Login({ onLogin }) {
  const [username, setUsername] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (username.trim()) {
      onLogin(username);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <input
        placeholder="Enter username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## export default

export default defines the main value exported by a file so it can be imported without curly braces.

## props

props are inputs to components
