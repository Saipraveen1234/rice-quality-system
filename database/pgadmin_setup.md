# How to View Your Database in pgAdmin

Since we fixed the user/role issue, follow these exact steps to connect:

1.  **Open pgAdmin**.
2.  If you have a failed server listed under "Servers", right-click and **Delete/Disconnect** it to start fresh (optional).
3.  Right-click on **Servers** > **Register** > **Server...**
4.  **General Tab**:
    *   **Name**: `Rice Quality Local` (or anything you like)
5.  **Connection Tab** (Use these EXACT settings):
    *   **Host name/address**: `localhost`
    *   **Port**: `5432`
    *   **Maintenance database**: `postgres`
    *   **Username**: `postgres`     <-- We just created this!
    *   **Password**: `postgres`     <-- We set this password.
    *   **Save password?**: [x] Yes
6.  Click **Save**.

## Verifying the Database
1.  Expand the new server (e.g., `Rice Quality Local`).
2.  Expand **Databases**.
3.  You should see **`rice_quality_db`**.
    *   This is the database we created for your project.
    *   It's currently empty (no tables yet), but it's ready!
