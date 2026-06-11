# 📁 Project Assets

This directory contains all project assets including network diagrams, images, and simulation files.

## 📂 Directory Structure

- **images/** - Network diagrams, topology images, and screenshots
- **packet-tracer/** - Cisco Packet Tracer simulation files

## 🖼️ Images Directory

Contains visual documentation of the network design:

### Network Diagrams
- `campus-network-topology.png` - Overall campus network topology
- `inter-campus-connectivity.png` - Inter-campus connection details  
- `security-architecture.png` - Security zone architecture
- `network-connectivity-diagram.png` - Detailed connectivity diagram
- `campus-network.png` - Campus network overview

### Image Standards
- **Format**: PNG preferred for diagrams, JPG for photos
- **Resolution**: Minimum 1920x1080 for diagrams
- **Naming**: Descriptive kebab-case naming
- **Quality**: High resolution for professional presentation

## 🎮 Packet Tracer Directory

Contains Cisco Packet Tracer simulation files:

### Simulation Files
- `campus-network-simulation.pkt` - Complete network simulation
  - Includes all devices and configurations
  - Demonstrates network functionality
  - Used for testing and validation

### Packet Tracer Standards
- **Version**: Compatible with Packet Tracer 8.0+
- **Naming**: Descriptive with version numbers if needed
- **Documentation**: Include simulation notes within PT file
- **Testing**: Verify all scenarios work before committing

## 📝 Usage Guidelines

### Adding New Images
1. **Optimize file size** while maintaining quality
2. **Use consistent styling** and color schemes
3. **Include legends** and labels for clarity
4. **Update documentation** references when adding images

### Updating Packet Tracer Files
1. **Test thoroughly** before saving
2. **Document changes** in commit messages
3. **Verify compatibility** with different PT versions
4. **Include configuration backups** if needed

### File Organization
```
assets/
├── images/
│   ├── topology/          # Network topology diagrams
│   ├── security/          # Security architecture diagrams  
│   ├── screenshots/       # Application screenshots
│   └── presentations/     # Presentation slides/images
└── packet-tracer/
    ├── main-simulation.pkt    # Primary network simulation
    ├── testing-scenarios/     # Individual test scenarios
    └── archived/              # Previous versions
```

## 🎨 Design Standards

### Color Scheme
- **Core Layer**: Dark Blue (#1f4e79)
- **Distribution Layer**: Medium Blue (#4472c4)  
- **Access Layer**: Light Blue (#8db4e2)
- **Security Zones**: Red variations (#c55a5a)
- **Connections**: Black or dark gray

### Typography  
- **Font**: Professional fonts (Arial, Calibri, Segoe UI)
- **Size**: Minimum 12pt for readability
- **Style**: Consistent bold/italic usage

### Symbols
- Use standard network symbols (Cisco or generic)
- Maintain consistent symbol sizing
- Include legend when using custom symbols

## 🔄 Version Control

### Git LFS (Large File Storage)
For large binary files:
```bash
# Track Packet Tracer files
git lfs track "*.pkt"

# Track large images  
git lfs track "assets/images/*.png"
git lfs track "assets/images/*.jpg"
```

### File Naming Versions
- Use semantic versioning for major updates
- Example: `campus-network-v2.1.pkt`
- Keep previous versions in `archived/` folder

## 📊 File Information

| File Type | Max Size | Format | Purpose |
|-----------|----------|--------|---------|
| Network Diagrams | 5MB | PNG | Documentation |
| Screenshots | 2MB | PNG/JPG | Tutorials |
| PT Simulations | 50MB | PKT | Testing/Demo |
| Presentations | 10MB | PNG/PDF | Training |

---

> 🎨 **Visual Excellence** | 📁 **Organized Assets** | 🎮 **Interactive Simulations**