import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.error("❌ Supabase environment variables are missing.");
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default supabase;



/*
export default supabase;

console.log("Supabase URL:", process.env.REACT_APP_SUPABASE_URL);
console.log("Supabase Key:", process.env.REACT_APP_SUPABASE_ANON_KEY);
import supabase from "./frontend/src/utils/supabase.js";

async function testSupabase() {
    console.log("Testing Supabase connection...");

    const { data, error } = await supabase.from("enhanceddata").select("*");
    if (error) {
        console.error("❌ Supabase Error:", error);
    } else {
        console.log("✅ Supabase Data:", data);
    }
}

testSupabase();
*/