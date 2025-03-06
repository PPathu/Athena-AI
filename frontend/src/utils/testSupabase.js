import supabase from "./supabase.js"; // Correct import (same folder)

async function testSupabase() {
    console.log("Testing Supabase connection...");

    const { data, error } = await supabase.from("bills").select("*");
    
    if (error) {
        console.error("❌ Supabase Error:", error);
    } else {
        console.log("✅ Supabase Data:", data);
    }
}

testSupabase();
