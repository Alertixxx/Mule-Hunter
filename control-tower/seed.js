const bcrypt = require('bcryptjs');

async function generate() {
    // This matches your app's "const hashedPassword = await bcrypt.hash(password, 10);"
    const hash = await bcrypt.hash("manyagupta", 10); 
    
    console.log("--- NEW HASH GENERATED ---");
    console.log(hash);
    console.log("--------------------------");
}

generate();