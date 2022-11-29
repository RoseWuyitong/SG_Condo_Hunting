import "./App.css";
import MainPageHeader from './my-image/MainPageHeader.png';
import Header from './Header';
import Footer from './Footer';


export default function App() {
  return (
    <div>
    <Header />

    <header>
      <img src={MainPageHeader} alt="MainPageHeader" width="100%"></img>
      <header class="text">
        <h1>SINGAPORE CONDO HUNTING GUIDE</h1>
        <p class="header-mandarin">新加坡公寓购买指南 &nbsp;
          <button class="button">Get Started &nbsp;<a class="mandarin">开始</a></button>
          <br />
          <ul class="vl">
            <li>
              <a href="CalculateMorgageAndTax.html">Calculate Morgage & Tax After Buy&nbsp; <a
                href="CalculateMorgageAndTax.html" class="mandarin">计算购房后月供以及税收总和</a></a>
            </li>
          </ul>
        </p>
      </header>
    </header>
    
    <Footer />
    </div>);
}



