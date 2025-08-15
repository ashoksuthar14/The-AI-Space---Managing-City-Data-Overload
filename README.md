# 🗺️ Traffic Insight Map

> A modern React.js web application that visualizes traffic data on interactive Google Maps with detailed location insights.

[Website Link](https://studio--nammaroute-navigator-6xdjf.us-central1.hosted.app/)


## 📖 Overview

Traffic Insight Map is a responsive web application that transforms location-based traffic data into an interactive mapping experience. Users can upload JSON files containing traffic information and visualize it through clickable markers on Google Maps, each revealing detailed insights about traffic conditions and their causes.

## ✨ Features

### Core Functionality
- **🗺️ Interactive Google Maps**: Renders a dynamic map centered on your city
- **📍 Smart Markers**: Automatically places markers based on coordinate data
- **ℹ️ Detailed Info Cards**: Click any marker to view comprehensive traffic insights
- **📂 Dynamic Data Loading**: Upload custom JSON files to update map data in real-time
- **🎨 Modern UI**: Clean, responsive design with Tailwind CSS

### Key Capabilities
| Feature | Description |
|---------|-------------|
| **Map Display** | Full-screen Google Maps integration with smooth interactions |
| **Marker Management** | Intelligent placement of markers with custom icons and clustering |
| **Information Panel** | Rich info windows displaying location details, traffic summaries, and causes |
| **File Upload** | Drag-and-drop JSON file support for dynamic data updates |
| **Responsive Design** | Works seamlessly across desktop, tablet, and mobile devices |

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v14.0.0 or higher) - [Download here](https://nodejs.org/)
- **npm** or **yarn** package manager
- **Google Maps API Key** - [Get your key](https://console.cloud.google.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/traffic-insight-map.git
cd traffic-insight-map

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key_here" > .env

# Start development server
npm start
```

Your application will be available at `http://localhost:3000`

## 📁 Project Structure

```
traffic-map-app/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── MapComponent.js      # Main map component
│   │   ├── InfoPanel.js         # Information display panel
│   │   └── FileUpload.js        # JSON file upload handler
│   ├── data/
│   │   └── sample-data.json     # Sample traffic data
│   ├── styles/
│   │   └── globals.css          # Global styles
│   ├── App.js                   # Main application component
│   └── index.js                 # Application entry point
├── .env                         # Environment variables
├── package.json                 # Project dependencies
└── README.md                    # Project documentation
```

## 📋 Data Format

The application expects JSON data in the following format:

```json
[
  {
    "location_name": "Basavanagudi",
    "coordinates": {
      "lat": 12.9405997,
      "lng": 77.5737633
    },
    "traffic_summary": "Recurring slowdowns and diversions",
    "causes": ["Ongoing metro construction", "Road maintenance"]
  },
  {
    "location_name": "Indiranagar",
    "coordinates": {
      "lat": 12.9718915,
      "lng": 77.6411545
    },
    "traffic_summary": "Heavy traffic during peak hours",
    "causes": ["Peak hours", "Narrow roads", "Commercial activity"]
  }
]
```

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `location_name` | String | Display name for the location |
| `coordinates` | Object | Latitude and longitude coordinates |
| `coordinates.lat` | Number | Latitude coordinate |
| `coordinates.lng` | Number | Longitude coordinate |
| `traffic_summary` | String | Brief description of traffic conditions |
| `causes` | Array | List of factors contributing to traffic issues |

## 🛠️ Technology Stack

- **Frontend Framework**: React.js 18+
- **Mapping Service**: Google Maps JavaScript API
- **Styling**: Tailwind CSS
- **Build Tool**: Create React App
- **Package Manager**: npm/yarn

## 🔧 Configuration

### Google Maps API Setup

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Maps JavaScript API**
4. Go to **Credentials** → **Create API Key**
5. Restrict your API key for security:
   - **Application restrictions**: HTTP referrers
   - **API restrictions**: Maps JavaScript API

### Environment Variables

Create a `.env` file in your project root:

```env
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
REACT_APP_MAP_CENTER_LAT=12.9716
REACT_APP_MAP_CENTER_LNG=77.5946
REACT_APP_DEFAULT_ZOOM=12
```

## 🎨 Customization

### Styling

The application uses Tailwind CSS for styling. You can customize the appearance by:

1. **Modifying Tailwind Configuration**: Edit `tailwind.config.js`
2. **Custom CSS Classes**: Add styles to `src/styles/globals.css`
3. **Component-level Styling**: Update className props in components

### Map Customization

```javascript
// Example: Custom map styles
const mapStyles = [
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#e9e9e9" }, { lightness: 17 }]
  }
  // Add more styles...
];

// Apply to map
const map = new google.maps.Map(mapRef.current, {
  zoom: 12,
  center: defaultCenter,
  styles: mapStyles
});
```

## 🚀 Deployment

### Netlify Deployment

```bash
# Build for production
npm run build

# Deploy to Netlify (install Netlify CLI first)
npm install -g netlify-cli
netlify deploy --prod --dir=build
```

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### GitHub Pages

```bash
# Install gh-pages
npm install --save-dev gh-pages

# Add to package.json scripts
"predeploy": "npm run build",
"deploy": "gh-pages -d build"

# Deploy
npm run deploy
```

## 🔮 Future Enhancements

- [ ] **Real-time Traffic Data**: Integration with live traffic APIs
- [ ] **Route Planning**: Add navigation between traffic points
- [ ] **Analytics Dashboard**: Traffic pattern analysis and reporting
- [ ] **Mobile App**: React Native version for mobile platforms
- [ ] **AI Integration**: Automatic traffic cause detection using computer vision
- [ ] **Multi-language Support**: Internationalization for global use
- [ ] **Offline Mode**: Progressive Web App capabilities

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Maps Platform](https://developers.google.com/maps) for mapping services
- [React](https://reactjs.org/) for the component framework
- [Tailwind CSS](https://tailwindcss.com/) for styling utilities
- [Create React App](https://create-react-app.dev/) for project bootstrapping

## 📞 Support

If you encounter any issues or have questions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/traffic-insight-map/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/traffic-insight-map/discussions)
- **Email**: your.email@example.com

---

<div align="center">
  <p>Made with ❤️ by [Your Name]</p>
  <p>⭐ Star this repository if you found it helpful!</p>
</div>
